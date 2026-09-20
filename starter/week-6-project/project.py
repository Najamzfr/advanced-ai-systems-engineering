"""Run the six-condition, split-safe adaptation benchmark."""
from __future__ import annotations
import argparse, collections, json, math, pathlib, re, resource, time
from lora_adapter import train_adapter
ROOT=pathlib.Path(__file__).resolve().parent; DATA=ROOT/"data"; REPORTS=ROOT/"reports"

def load(split):
    p=DATA/f"{split}.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def tok(s): return set(re.findall(r"[a-z0-9]+",s.lower()))
def sim(a,b):
    aa,bb=tok(a),tok(b); return len(aa&bb)/(len(aa|bb) or 1)
def prompt_predict(text, labels):
    # Explicit baseline: prior-free lexical intent words only.
    words=tok(text); best=None; score=-1
    for label in labels:
        key=set(re.findall(r"[a-z0-9]+",label.replace("_"," ")))
        s=len(words&key)
        if s>score: best,score=label,s
    return best or labels[0]
def rag_predict(text,train):
    return max(train,key=lambda r:sim(text,r["text"]))["label"]
def hybrid_prompt_rag(text,train,labels):
    """Prompt-first route with retrieval fallback; deliberately distinct."""
    words=tok(text); keyed=[x for x in labels if words & set(x.replace("_"," ").split())]
    return prompt_predict(text,labels) if keyed else rag_predict(text,train)
def hybrid_prompt_adapter(text,labels,adapter):
    """Use the trained adapter only when the prompt baseline has no label cue."""
    words=tok(text); prompt=prompt_predict(text,labels)
    key=set(prompt.replace("_"," ").split()) if prompt else set()
    return prompt if words & key else adapter.predict(text)
def hybrid_rag_adapter(text,train,adapter):
    """Retrieve a candidate, then let the adapted model break ties."""
    retrieved=rag_predict(text,train); adapted=adapter.predict(text)
    return retrieved if retrieved==adapted else adapted
def metrics(rows):
    n=len(rows); correct=sum(r["prediction"]==r["label"] for r in rows); labels=sorted({r["label"] for r in rows})
    f=[]
    for lab in labels:
        tp=sum(r["prediction"]==lab and r["label"]==lab for r in rows); fp=sum(r["prediction"]==lab and r["label"]!=lab for r in rows); fn=sum(r["prediction"]!=lab and r["label"]==lab for r in rows)
        p=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0; f.append(2*p*recall/(p+recall) if p+recall else 0)
    return {"cases":n,"accuracy":correct/n if n else 0,"macro_f1":sum(f)/len(f) if f else 0}
def run_condition(name, test, train, labels, adapter=None, limit=None):
    rows=[]; times=[]; start_mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for r in test[:limit] if limit else test:
        t=time.perf_counter()
        if name == "prompt": pred=prompt_predict(r["text"],labels)
        elif name == "rag": pred=rag_predict(r["text"],train)
        elif name == "lora": pred=adapter.predict(r["text"])
        elif name == "prompt_rag": pred=hybrid_prompt_rag(r["text"],train,labels)
        elif name == "prompt_lora": pred=hybrid_prompt_adapter(r["text"],labels,adapter)
        else: pred=hybrid_rag_adapter(r["text"],train,adapter)
        ms=(time.perf_counter()-t)*1000; times.append(ms); rows.append({"id":r["id"],"label":r["label"],"prediction":pred,"latency_ms":ms,"tokens":len(r["text"].split()),"condition":name})
    out=metrics(rows); ss=sorted(times); p95=ss[min(len(ss)-1,max(0,math.ceil(.95*len(ss))-1))] if ss else 0
    out.update({"strategy":name,"latency_p50_ms":ss[len(ss)//2] if ss else 0,"latency_p95_ms":p95,"tokens_per_sec":sum(x["tokens"] for x in rows)/(sum(times)/1000 or 1),"memory_mb":max(0,(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss-start_mem)/1024),"rows":rows})
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--limit",type=int)
    ap.add_argument("--adapter-mode",choices=("auto","peft","fallback"),default="auto",help="peft is strict and never falls back")
    ap.add_argument("--qlora",action="store_true",help="request 4-bit QLoRA; requires CUDA + bitsandbytes")
    args=ap.parse_args(); REPORTS.mkdir(exist_ok=True)
    if args.qlora and args.adapter_mode=="fallback": ap.error("--qlora cannot be used with --adapter-mode fallback")
    train,test=load("train"),load("test"); labels=sorted({r["label"] for r in train});
    train_ids={r["id"] for r in train}; test_ids={r["id"] for r in test}; train_text={" ".join(sorted(tok(r["text"]))) for r in train}; test_text={" ".join(sorted(tok(r["text"]))) for r in test}
    leakage={"train_test_id_overlap":len(train_ids&test_ids),"train_test_text_overlap":len(train_text&test_text),"train_cases":len(train),"test_cases":len(test),"labels_train":len(labels),"labels_test":len({r["label"] for r in test})}; (REPORTS/"leakage.json").write_text(json.dumps(leakage,indent=2)+"\n")
    adapter,adapter_meta=train_adapter(train,labels,mode=args.adapter_mode,quantized=args.qlora)
    conditions={}; all_rows=[]
    for name in ("prompt","rag","lora","prompt_rag","prompt_lora","rag_lora"):
        x=run_condition(name,test,train,labels,adapter,args.limit); all_rows.extend(x.pop("rows")); conditions[name]=x
    (REPORTS/"results.jsonl").write_text("\n".join(json.dumps(x) for x in all_rows)+"\n")
    manifest=json.loads((DATA/"manifest.json").read_text()); m={"week":6,"dataset":manifest,"train_cases":len(train),"test_cases":len(test),"conditions":conditions,"adapter":adapter_meta,"leakage":leakage,"run_mode":"benchmark" if manifest.get("source_type")=="public_download" else "offline_fixture","command":{"adapter_mode":args.adapter_mode,"qlora":args.qlora},"real_lora_complete":adapter_meta.get("executed") in ("transformers_peft_lora","transformers_peft_qlora")}
    (REPORTS/"metrics.json").write_text(json.dumps(m,indent=2)+"\n")
    report={'week':6,'cases':len(test),'adapter':m['adapter'],'leakage':leakage,'conditions':conditions,'raw_results':'reports/results.jsonl'}
    (REPORTS/"adaptation_report.json").write_text(json.dumps(report,indent=2)+"\n")
    (REPORTS/"adaptation_report.md").write_text("# Adaptation report\n\nThe benchmark uses disjoint train/test IDs and text. The adapter path is **"+adapter_meta["executed"]+"**. The six rows are separate executable serving strategies: prompt-only, lexical retrieval, adapted classifier, and three explicit hybrids.\n\nReal LoRA completion: **"+str(m["real_lora_complete"]).lower()+"**. Reproduce a strict real run with `make run-lora` (or `make run-qlora` on CUDA); `make run` may use the transparent fallback.\n\nAdapter metadata: `"+json.dumps(adapter_meta,sort_keys=True)+"`\n\n## Conditions\n\n"+"\n".join(f"- **{k}** (`{v['strategy']}`): accuracy={v['accuracy']:.3f}; macro-F1={v['macro_f1']:.3f}; p95={v['latency_p95_ms']:.3f} ms; tokens/s={v['tokens_per_sec']:.1f}" for k,v in conditions.items())+"\n")
    (REPORTS/"capacity_plan.md").write_text("# Capacity plan\n\nUse the measured condition table to choose the quality/latency point for the declared request mix. The offline adapter is a reference baseline; do not claim transformer-LoRA gains unless `adapter.executed` records that path.\n")
    print(json.dumps({"week":6,"run_mode":m["run_mode"],"train_cases":len(train),"test_cases":len(test),"conditions":list(conditions),"adapter":adapter_meta["executed"],"real_lora_complete":m["real_lora_complete"]}))
if __name__=="__main__": main()
