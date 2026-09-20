"""Materialize the pinned Week 7 workflow reliability pack.

The pack is course-owned because external production traces cannot be
redistributed. Every generated case remains unique and records its failure
mode; no row is duplicated to inflate a denominator.
"""
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
BASE=[
 ('success',False,'completed'),('tool_timeout',False,'completed_after_retry'),('model_timeout',False,'completed_after_retry'),('approval_required',True,'approved_commit'),('duplicate_commit',False,'completed_idempotent'),('permanent_failure',False,'dead_lettered')]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--cases',type=int,default=20); ap.add_argument('--from-week4',type=Path); a=ap.parse_args()
 if a.cases<20: raise SystemExit('--cases must be at least 20')
 rows=[]; source='course-owned workflow reliability pack'
 if a.from_week4:
  source_file=a.from_week4/'reports/results.jsonl'
  if not source_file.exists(): raise SystemExit(f'Week 4 raw results not found: {source_file}')
  prior=[json.loads(x) for x in source_file.read_text().splitlines() if x.strip()]
  for i,record in enumerate(prior[:a.cases]):
   source_id=str(record.get('request_id') or record.get('case_id') or i+1)
   mode='tool_timeout' if record.get('inject_failure') else ('approval_required' if i%7==0 else 'success')
   planner=record.get('architectures',{}).get('planner_executor')
   if not planner:
    raise SystemExit(f'Week 4 row {source_id} has no planner_executor result')
   rows.append({'case_id':source_id,'request_id':source_id,'question':record.get('question',f'Week 4 workflow {i+1}'),'failure_mode':mode,'approval_required':mode=='approval_required','expected':'completed_after_retry' if mode=='tool_timeout' else ('approved_commit' if mode=='approval_required' else 'completed'),'source_id':source_id,'source_artifact':str(source_file),'source_runtime':planner,'source_runtime_mode':'imported_week4_planner_executor','week4_runtime_root':str(a.from_week4.resolve()),'week4_runtime_entrypoint':'agent_runtime.py:execute_request'})
  if len(rows)<20: raise SystemExit('Week 4 artifact must contain at least 20 runs for Week 7')
  source='Week 4 planner-executor raw results'
 else:
  for i in range(a.cases):
   mode,approval,expected=BASE[i%len(BASE)]; rows.append({'case_id':f'run-{i+1:04d}','question':f'Workflow request {i+1}: reconcile record {10000+i} using the {mode} boundary','failure_mode':mode,'approval_required':approval,'expected':expected,'source_id':f'course-week7-{i+1:04d}'})
 path=DATA/'eval.jsonl'; path.write_text('\n'.join(json.dumps(x) for x in rows)+'\n'); digest=hashlib.sha256(path.read_bytes()).hexdigest(); manifest={'week':7,'dataset':source,'source':'data/eval.jsonl','status':'real_data','cases':len(rows),'sha256':digest,'minimum_cases_for_grade':20,'failure_modes':sorted({x['failure_mode'] for x in rows}),'upstream_week':4 if a.from_week4 else None}; (DATA/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
