"""Judge prompt and evaluation path for the audit sample."""
import json
import os
import urllib.request

CLASSIFIER_SYSTEM_PROMPT = "Classify a BANKING77 customer message. Return JSON only with one key, label. Use the canonical BANKING77 intent name; never add punctuation."
JUDGE_PROMPT = """You are an evaluation judge for a customer-support intent classifier.
Given the message, gold label, and model label, return JSON with judge_label,
agree (boolean), and rationale. Do not invent a new label. A correct answer
must exactly match the gold canonical intent.
Message: {text}
Gold label: {gold}
Model label: {prediction}
"""

def judge_case(case, prediction, remote=False):
    if remote or os.getenv("WEEK1_JUDGE", "offline").lower() == "openai":
        if not os.getenv("OPENAI_API_KEY"): raise RuntimeError("WEEK1_JUDGE=openai requires OPENAI_API_KEY")
        body = {"model": os.getenv("WEEK1_JUDGE_MODEL", "gpt-4o-mini"), "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Return only valid JSON."}, {"role": "user", "content": JUDGE_PROMPT.format(text=case["text"], gold=case["label"], prediction=prediction)}]}
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions"; req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as response: return json.loads(json.loads(response.read().decode())["choices"][0]["message"]["content"])
    return {"judge_label": prediction, "agree": prediction == case["label"], "rationale": "Deterministic audit judge: exact canonical-label comparison."}
