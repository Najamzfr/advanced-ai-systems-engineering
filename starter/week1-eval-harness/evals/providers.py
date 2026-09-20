"""Provider adapters for the Week 1 evaluation harness."""
import json
import os
import re
import time
import urllib.request

MODEL_NAMES = ["baseline-v1", "robust-v2"]
_SYNONYMS = {"arrive": {"delivery", "deliver", "waiting", "late", "where"}, "estimate": {"when", "long", "time", "days"}, "pending": {"processing", "waiting"}, "declined": {"decline", "rejected", "reject", "failed"}, "not": {"unknown", "unrecognised", "unrecognized", "dont", "didnt"}, "recognised": {"recognised", "recognized", "unknown", "unfamiliar"}, "reverted": {"reversal", "reversed", "returned"}, "cash": {"atm", "withdrawal"}, "top": {"topup", "recharge", "add"}}

def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower().replace("-", " ")))

def _intent_tokens(intent):
    tokens = set(intent.split("_"))
    return tokens | {item for token in tokens for item in _SYNONYMS.get(token, ())}

def _offline_label(model, text):
    tokens = _tokens(text)
    if "card" in tokens and ({"waiting", "late", "delivery"} & tokens) and not ({"payment", "pay"} & tokens):
        return "card_arrival" if not ({"when", "long", "days", "estimate"} & tokens) else "card_delivery_estimate"
    phrase_rules = {"cash_withdrawal_not_recognised": ("cash", "withdrawal", "not", "recognise"), "card_payment_not_recognised": ("card", "payment", "not", "recognise"), "reverted_card_payment": ("reverted", "card", "payment"), "cash_withdrawal_charge": ("cash", "withdrawal", "charge"), "verify_my_identity": ("verify", "identity")}
    candidates = [intent for intent, phrase in phrase_rules.items() if all(any(part in token for token in tokens) for part in phrase)]
    if candidates:
        return max(candidates, key=lambda item: len(tokens & _intent_tokens(item))) if model == "robust-v2" else sorted(candidates)[0]
    labels = ["card_arrival", "card_delivery_estimate", "pending_cash_withdrawal", "declined_cash_withdrawal", "cash_withdrawal_not_recognised", "cash_withdrawal_charge", "wrong_exchange_rate_for_cash_withdrawal", "pending_card_payment", "declined_card_payment", "card_payment_not_recognised", "reverted_card_payment", "pending_top_up", "top_up_reverted", "top_up_failed", "verify_top_up", "verify_my_identity", "cash_withdrawal_amount"]
    best_score, best_label = max(((len(tokens & _intent_tokens(label)), label) for label in labels), key=lambda pair: (pair[0], pair[1]))
    return best_label if best_score else "unknown"

class OfflineProvider:
    name = "offline-deterministic"
    def __init__(self, model): self.model = model
    def classify(self, text):
        started = time.perf_counter(); label = _offline_label(self.model, text)
        return {"label": label, "schema_valid": isinstance(label, str) and bool(label), "latency_ms": round((time.perf_counter() - started) * 1000, 4), "provider": self.name, "input_tokens": len(_tokens(text)), "output_tokens": 1, "cost_usd": 0.0}

class OpenAICompatibleProvider:
    """Stdlib OpenAI-compatible chat-completions adapter."""
    name = "openai-compatible"
    def __init__(self, model):
        self.model = os.getenv(f"WEEK1_{model.upper().replace('-', '_')}_MODEL", model); self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"); self.api_key = os.environ["OPENAI_API_KEY"]
    def classify(self, text):
        from .judge import CLASSIFIER_SYSTEM_PROMPT
        body = {"model": self.model, "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT}, {"role": "user", "content": text}]}
        request = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"}); started = time.perf_counter()
        with urllib.request.urlopen(request, timeout=60) as response: payload = json.loads(response.read().decode())
        parsed = json.loads(payload["choices"][0]["message"]["content"]); usage = payload.get("usage", {})
        # OpenAI-compatible APIs generally return token usage, not a cost field.
        # Keep the price assumption explicit so a cost comparison cannot silently
        # become zero just because the provider omits billing metadata.
        input_tokens = int(usage.get("prompt_tokens", 0) or 0)
        output_tokens = int(usage.get("completion_tokens", 0) or 0)
        input_rate = float(os.getenv("WEEK1_INPUT_COST_PER_1K_USD", "0"))
        output_rate = float(os.getenv("WEEK1_OUTPUT_COST_PER_1K_USD", "0"))
        estimated_cost = (input_tokens / 1000 * input_rate) + (output_tokens / 1000 * output_rate)
        return {"label": parsed["label"], "schema_valid": isinstance(parsed.get("label"), str), "latency_ms": round((time.perf_counter() - started) * 1000, 4), "provider": self.name, "model_id": self.model, "input_tokens": input_tokens, "output_tokens": output_tokens, "cost_usd": round(estimated_cost, 10), "cost_basis": {"input_per_1k_usd": input_rate, "output_per_1k_usd": output_rate, "source": "environment price assumption"}}

def provider_for(model):
    mode = os.getenv("WEEK1_PROVIDER", "offline").lower()
    if mode in {"openai", "api", "remote"}:
        if not os.getenv("OPENAI_API_KEY"): raise RuntimeError("WEEK1_PROVIDER=openai requires OPENAI_API_KEY")
        return OpenAICompatibleProvider(model)
    return OfflineProvider(model)

def predict(model: str, text: str):
    if model not in MODEL_NAMES: raise ValueError(f"unknown model {model}; choose from {MODEL_NAMES}")
    return provider_for(model).classify(text)

def available_models(): return MODEL_NAMES.copy()
