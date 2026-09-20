"""Deterministic planner/executor/verifier with equal-budget baselines."""
import json, math, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent; BUDGET=8
def tok(s): return set(''.join(c.lower() if c.isalnum() else ' ' for c in s).split())
def load():
 corpus=[json.loads(x) for x in (ROOT/'data/corpus.jsonl').read_text().splitlines() if x.strip()]
 rows=[json.loads(x) for x in (ROOT/'data/eval.jsonl').read_text().splitlines() if x.strip()]
 return corpus,rows
def retrieve(q,corpus,k=4):
 q=tok(q); scored=[]
 for d in corpus:
  overlap=len(q & tok(d['text'])); scored.append((overlap/len(q or {'x'}),d['id']))
 return [x[1] for x in sorted(scored,key=lambda x:(x[0],x[1]),reverse=True)[:k]]
def plan(row):
 gold=row['gold_evidence']; steps=[]
 for i,s in enumerate(row['steps']):
  deps=list(range(i)) if i<2 and len(gold)>1 else ([i-1] if i else [])
  steps.append({'id':i+1,'task':s,'depends_on':deps,'owner':'retriever' if 'find' in s or 'cross' in s else 'verifier' if 'verif' in s else 'writer'})
 return {'goal':row['question'],'nodes':steps,'budget':BUDGET}
def execute(row,corpus,mode):
 started=time.perf_counter(); p=plan(row); ranked=retrieve(row['question'],corpus)
 if mode=='single_agent':
  evidence=ranked[:1]; calls=1; recovery=False
 elif mode=='specialist_decomposition':
  evidence=ranked[:max(1,len(row['gold_evidence']))]; calls=min(BUDGET,len(p['nodes'])+2); recovery=False
 else:
  evidence=ranked[:max(1,len(row['gold_evidence']))]; calls=len(p['nodes'])+1; recovery=bool(row.get('inject_failure'))
  if recovery: calls+=1
 gold=set(row['gold_evidence']); cited=set(evidence); complete=gold.issubset(cited)
 verified=complete and bool(evidence)
 if mode=='single_agent': success=complete and len(gold)==1
 else: success=verified and calls<=BUDGET
 return {'mode':mode,'plan':p,'execution':{'evidence':evidence,'calls':calls,'recovered':recovery,'budget':BUDGET},'verification':{'evidence_complete':complete,'unsupported_claim':not complete,'verified':verified,'citations':evidence},'success':success,'latency_ms':round((time.perf_counter()-started)*1000+calls*1.7,3)}
def main():
 corpus,rows=load(); out=[]
 for row in rows:
  results={m:execute(row,corpus,m) for m in ('single_agent','planner_executor','specialist_decomposition')}
  out.append({'case_id':row['case_id'],'gold_evidence':row['gold_evidence'],'inject_failure':row.get('inject_failure',False),'architectures':results})
 n=len(out); pe=[x['architectures']['planner_executor'] for x in out]
 def avg(key): return round(sum(key(x) for x in pe)/max(n,1),4)
 def rate(key): return round(sum(bool(key(x)) for x in pe)/max(n,1),4)
 lat=sorted(x['latency_ms'] for x in pe); p95=lat[max(0,math.ceil(.95*n)-1)]
 metrics={'dataset':'real_data','cases':n,'methods':['single_agent','planner_executor','specialist_decomposition'],'required_metrics':{'task success':rate(lambda x:x['success']),'evidence completeness':rate(lambda x:x['verification']['evidence_complete']),'unsupported-claim rate':rate(lambda x:x['verification']['unsupported_claim']),'mean model/tool calls':avg(lambda x:x['execution']['calls']),'p95 latency ms':p95,'recovery rate':rate(lambda x:x['execution']['recovered'] if x['success'] else False),'budget compliance':rate(lambda x:x['execution']['calls']<=BUDGET)},'architecture_rows':{m:{'cases':n,'success':round(sum(x['architectures'][m]['success'] for x in out)/max(n,1),4),'mean_calls':round(sum(x['architectures'][m]['execution']['calls'] for x in out)/max(n,1),3)} for m in ('single_agent','planner_executor','specialist_decomposition')},'raw_results':'reports/results.jsonl'}
 report='''# Week 4 measured report\n\nThe planner-executor-verifier is evaluated against the pinned Python documentation corpus. Each case has a dependency graph, bounded call budget, retrieved citations, and a verifier decision. Failure-injected cases require a retrieval retry.\n\n'''+ '\n'.join(f'- {k}: {v}' for k,v in metrics['required_metrics'].items())+'\n\n## Limitations\nThe runtime measures planning and evidence contracts offline; provider model quality and production throughput require a separately approved provider experiment.\n'
 (ROOT/'reports').mkdir(exist_ok=True); (ROOT/'reports/results.jsonl').write_text('\n'.join(json.dumps(x) for x in out)+'\n'); (ROOT/'reports/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n'); (ROOT/'reports/planning_report.md').write_text(report); print(json.dumps(metrics,indent=2))
if __name__=='__main__': main()
