import argparse, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MIN_CASES=200
METHODS={"bm25","dense","hybrid","hybrid_rerank","document_level","long_context"}
REQUIRED={"Recall@5","MRR@5","citation precision","answer correctness","latency p95","token cost"}
def load():
    manifest=json.loads((ROOT/"data/manifest.json").read_text()) if (ROOT/"data/manifest.json").exists() else {}
    metrics=json.loads((ROOT/"reports/metrics.json").read_text()) if (ROOT/"reports/metrics.json").exists() else {}
    raw=[json.loads(x) for x in (ROOT/"reports/results.jsonl").read_text().splitlines() if x.strip()] if (ROOT/"reports/results.jsonl").exists() else []
    return manifest,metrics,raw
def ev(ok,observed,required,msg): return {"passed":bool(ok),"observed":observed,"required":required,"message":msg}
def checks():
    manifest,m,raw=load(); vals=m.get("required_metrics",{}); ids=[x.get("case_id") for x in raw]
    methods=all(set(x.get("methods",{}))==METHODS and all("top_k" in x["methods"][k] and "latency_ms" in x["methods"][k] for k in METHODS) for x in raw)
    paired=all(x.get("gold_evidence_id") and x.get("question_id") for x in raw)
    cited_answers=all(
        x.get("cited_answer",{}).get("mode")=="extractive"
        and x.get("cited_answer",{}).get("citations")
        and all(c.get("evidence_id") in x.get("methods",{}).get("hybrid_rerank",{}).get("top_k",[]) for c in x.get("cited_answer",{}).get("citations",[]))
        for x in raw
    )
    numeric=all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in vals.values())
    return {
      "metrics_file":ev(bool(m),"present" if m else "missing","reports/metrics.json","run the evaluator"),
      "qasper_provenance":ev(manifest.get("status")=="real_data" and "QASPER" in manifest.get("dataset","") ,manifest.get("dataset","missing"),"QASPER real_data","fetch the pinned corpus"),
      "minimum_cases":ev(len(raw)>=MIN_CASES,len(raw),f">= {MIN_CASES}","evaluate the declared corpus slice"),
      "unique_cases":ev(len(ids)==len(set(ids)) and len(ids)==m.get("cases",0),len(set(ids)),"one unique ID per metric case","preserve case identity"),
      "required_metrics":ev(set(vals)==REQUIRED,sorted(vals),sorted(REQUIRED),"emit all six required metrics"),
      "numeric_metrics":ev(numeric,vals,"numeric measured values","derive metrics from raw evidence"),
      "retrieval_methods":ev(methods,"six per-case method results" if methods else "missing or incomplete",sorted(METHODS),"run all six retrieval configurations"),
      "oracle_pairing":ev(paired,"question, gold evidence and oracle result" if paired else "missing", "separate retrieval from answer correctness","retain oracle-context evidence"),
      "cited_answers":ev(cited_answers,"extractive citations" if cited_answers else "missing citations", "one source-backed cited answer per case", "preserve citation evidence with each retrieval result"),
      "method_rows":ev(set(m.get("method_rows",{}))==METHODS,sorted(m.get("method_rows",{})),sorted(METHODS),"include comparable method rows"),
      "artifact":ev((ROOT/"reports/retrieval_decision.md").exists() and (ROOT/"reports/retrieval_decision.md").stat().st_size>=300,"reports/retrieval_decision.md","measured retrieval decision","write a decision report"),
    }
def grade():
    c=checks(); errors=[f"{k}: {v['message']}" for k,v in c.items() if not v['passed']]; out={"status":"pass" if not errors else "fail","summary":{"passed":sum(v['passed'] for v in c.values()),"total":len(c)},"checks":c,"errors":errors}; (ROOT/"reports/grade.json").write_text(json.dumps(out,indent=2)+"\n")
    if errors: raise SystemExit("GRADE FAIL\n- " + "\n- ".join(errors))
    print("GRADE PASS\nMachine-readable result: reports/grade.json")
def step(n):
    manifest,m,raw=load(); vals=m.get("required_metrics",{}); ids=[x.get("case_id") for x in raw]
    tests={
      1: (bool(manifest.get("dataset")) and bool(manifest.get("sha256")),manifest.get("dataset","missing"),"manifest dataset and hash"),
      2: (manifest.get("status")=="real_data" and "QASPER" in manifest.get("dataset","") ,manifest.get("status"),"QASPER real_data manifest"),
      3: (len(raw)>=MIN_CASES,len(raw),f">= {MIN_CASES} raw cases"),
      4: (len(ids)==len(set(ids))==m.get("cases",-1),len(set(ids)),"unique IDs equal metrics cases"),
      5: (all(x.get("question_id") and x.get("gold_evidence_id") for x in raw),"question/evidence pairs" ,"every row retains provenance"),
      6: (all(set(x.get("methods",{}))==METHODS for x in raw),sorted(METHODS),"all six methods per case"),
      7: (all(all(x["methods"][k].get("rank") is None or x["methods"][k]["rank"]>=1 for k in METHODS) for x in raw),"rank values valid","ranked evidence"),
      8: (set(m.get("method_rows",{}))==METHODS,sorted(m.get("method_rows",{})),"comparable method rows"),
      9: (set(vals)==REQUIRED,sorted(vals),"all required metrics"),
      10: (all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in vals.values()),vals,"numeric observed metrics"),
      11: ((ROOT/"reports/retrieval_decision.md").exists() and "oracle" in (ROOT/"reports/retrieval_decision.md").read_text().lower() and all(x.get("cited_answer",{}).get("citations") for x in raw),"oracle-context explanation and cited answer evidence","failure boundary and oracle control"),
      12: (not any(not x['passed'] for x in checks().values()),"all checks pass","complete evidence-derived report"),
    }
    ok,obs,req=tests[n]
    if not ok: raise SystemExit(f"STEP FAIL {n}: observed {obs}; required {req}")
    print(f"STEP PASS {n}: observed {obs}; required {req}")
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["setup","grade"]+[f"check-step-{i}" for i in range(1,13)]); a=ap.parse_args()
    if a.command=="setup": print("setup: ready; run python scripts/fetch_data.py --cases 200")
    elif a.command=="grade": grade()
    else: step(int(a.command.rsplit("-",1)[1]))
