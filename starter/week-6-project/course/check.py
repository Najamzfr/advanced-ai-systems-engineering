from __future__ import annotations
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; R=ROOT/"reports"; D=ROOT/"data"
def read():
    p=R/"metrics.json"
    if not p.exists(): raise SystemExit("FAIL: reports/metrics.json is missing; run make run")
    return json.loads(p.read_text())
def checks(m):
    c=m.get("conditions",{}); leak=m.get("leakage",{}); rows=[json.loads(x) for x in (R/"results.jsonl").read_text().splitlines() if x.strip()] if (R/"results.jsonl").exists() else []
    return [
      ("train/test split is present and non-empty", m.get("train_cases",0)>0 and m.get("test_cases",0)>0),
      ("all six named conditions were executed", set(c)>=set(("prompt","rag","lora","prompt_rag","prompt_lora","rag_lora"))),
      ("raw result count equals condition case denominators", len(rows)==sum(v.get("cases",0) for v in c.values())),
      ("raw result IDs are unique within each condition", len({(x.get("condition"),x.get("id")) for x in rows})==len(rows)),
      ("metrics are derived numeric accuracy and macro-F1", all(isinstance(v.get("accuracy"), (int,float)) and isinstance(v.get("macro_f1"),(int,float)) for v in c.values())),
      ("latency and throughput were measured", all(v.get("latency_p95_ms",0)>=0 and v.get("tokens_per_sec",0)>0 for v in c.values())),
      ("no train/test ID or normalized text leakage", leak.get("train_test_id_overlap")==0 and leak.get("train_test_text_overlap")==0),
      ("real PEFT LoRA or QLoRA was executed (fallback does not complete this step)", m.get("adapter",{}).get("executed") in ("transformers_peft_lora","transformers_peft_qlora") and m.get("adapter",{}).get("is_transformer_lora") is True and m.get("real_lora_complete") is True),
      ("manifest records source provenance and checksums", bool(m.get("dataset",{}).get("source_type")) and bool(m.get("dataset",{}).get("sha256"))),
      ("adaptation report exists", (R/"adaptation_report.md").exists() and (R/"adaptation_report.md").stat().st_size>200),
      ("raw leakage evidence exists", (R/"leakage.json").exists()),
      ("test denominator is at least 300 cases", m.get("test_cases",0)>=300),
    ]
def main():
    if len(sys.argv)<2: raise SystemExit("usage: python -m course.check step N|grade")
    m=read(); results=checks(m)
    if sys.argv[1]=="step":
        n=int(sys.argv[2]); ok=0<n<=len(results) and results[n-1][1]; print(("PASS" if ok else "FAIL")+f": step {n} — {results[n-1][0] if 0<n<=len(results) else 'unknown step'}"); raise SystemExit(0 if ok else 1)
    failed=[f"{i+1}: {msg}" for i,(msg,ok) in enumerate(results) if not ok]; print("PASS: all Week 6 evidence checks" if not failed else "FAIL:\n"+"\n".join(failed)); raise SystemExit(0 if not failed else 1)
if __name__=="__main__": main()
