import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MIN_CASES=25
REQ={'task success','evidence completeness','unsupported-claim rate','mean model/tool calls','p95 latency ms','recovery rate','budget compliance'}
def load():
 m=json.loads((ROOT/'data/manifest.json').read_text()) if (ROOT/'data/manifest.json').exists() else {}
 x=json.loads((ROOT/'reports/metrics.json').read_text()) if (ROOT/'reports/metrics.json').exists() else {}
 rs=[json.loads(z) for z in (ROOT/'reports/results.jsonl').read_text().splitlines()] if (ROOT/'reports/results.jsonl').exists() else []
 return m,x,rs
def ev(ok,obs,req,msg): return {'passed':bool(ok),'observed':obs,'required':req,'message':msg}
def checks():
 m,x,rs=load(); vals=x.get('required_metrics',{}); modes={'single_agent','planner_executor','specialist_decomposition'}
 distinct=len({r.get('case_id') for r in rs})==len(rs) and len(rs)==x.get('cases',-1)
 shape=all(set(r.get('architectures',{}))>=modes and all('plan' in r['architectures'][z] and 'verification' in r['architectures'][z] for z in modes) for r in rs)
 graph=all(all(node.get('depends_on') is not None for node in r['architectures']['planner_executor']['plan']['nodes']) for r in rs)
 derived=shape and graph and distinct and all(r['architectures']['planner_executor']['execution']['calls']<=8 for r in rs)
 return {'metrics_file':ev(bool(x),'present' if x else 'missing','reports/metrics.json','run make run'),'real_data':ev(m.get('status')=='real_data',m.get('status'),'real_data','run make setup'),'minimum_cases':ev(m.get('cases',0)>=MIN_CASES,m.get('cases',0),f'>= {MIN_CASES}','materialise at least 20 cases'),'raw_evidence':ev(bool(rs),len(rs),'reports/results.jsonl','preserve raw evidence'),'unique_cases':ev(distinct,len({r.get("case_id") for r in rs}),x.get('cases'),'unique rows equal reported cases'),'week4_contract':ev(shape,'planner, executor, verifier, specialist','all architecture outputs','run project.py'),'dependency_graph':ev(graph,'dependency lists present','every plan node has dependencies','run project.py'),'derived_execution':ev(derived,'calls and verification computed from raw rows','bounded calls and verification','do not hardcode metrics'),'required_metrics':ev(set(vals)==REQ,sorted(vals),sorted(REQ),'write all required metrics'),'report':ev((ROOT/'reports/planning_report.md').exists() and (ROOT/'reports/planning_report.md').stat().st_size>250,'planning_report.md','measured report','write the report')}
def grade():
 c=checks(); errors=[f'{k}: {v["message"]}' for k,v in c.items() if not v['passed']]; result={'status':'pass' if not errors else 'fail','checks':c,'summary':{'passed':sum(v['passed'] for v in c.values()),'total':len(c)},'errors':errors}; (ROOT/'reports/grade.json').write_text(json.dumps(result,indent=2)+'\n'); print('GRADE PASS' if not errors else 'GRADE FAIL');
 if errors: raise SystemExit(1)
def step(i):
 c=checks(); keys=['metrics_file','real_data','minimum_cases','raw_evidence','unique_cases','week4_contract','dependency_graph','derived_execution','required_metrics','report','week4_contract','derived_execution']; k=keys[i-1]; v=c[k]; print(f'STEP {"PASS" if v["passed"] else "FAIL"} {i}: {v["message"]}\n- observed: {v["observed"]}\n- required: {v["required"]}'); raise SystemExit(0 if v['passed'] else 1)
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('command'); a=p.parse_args(); grade() if a.command=='grade' else step(int(a.command.rsplit('-',1)[1]))
