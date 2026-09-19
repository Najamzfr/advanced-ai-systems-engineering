import re
import time


INTENTS = {
    "card_arrival": ("card", "arrive", "delivery", "waiting"),
    "verify_my_identity": ("verify", "identity", "id", "document"),
    "cash_withdrawal_charge": ("cash", "withdrawal", "atm", "twice"),
    "card_payment_fee_charged": ("fee", "charged", "payment"),
    "cash_withdrawal_not_recognised": ("cash", "withdrawal", "recognise", "unknown"),
    "cash_withdrawal_wrong_exchange_rate": ("cash", "withdrawal", "exchange", "rate"),
    "cash_withdrawal_amount": ("cash", "withdrawal", "amount"),
    "cash_withdrawal_charge": ("cash", "withdrawal", "charge"),
}


def _scores(text: str):
    tokens = set(re.findall(r"[a-z_]+", text.lower()))
    return {intent: len(tokens.intersection(words)) for intent, words in INTENTS.items()}


def predict(model: str, text: str):
    started = time.perf_counter()
    scores = _scores(text)
    if model == "robust-v2":
        # The second adapter intentionally handles multi-token concepts better.
        scores["cash_withdrawal_charge"] += int("twice" in text.lower())
        scores["verify_my_identity"] += int("passport" in text.lower())
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = "unknown"
    elapsed_ms = round((time.perf_counter() - started) * 1000, 4)
    return {"label": best, "schema_valid": isinstance(best, str), "latency_ms": elapsed_ms}


def available_models():
    return ["baseline-v1", "robust-v2"]
