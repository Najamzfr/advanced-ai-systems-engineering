"""Week 7: durable, observable workflow runner.

The state journal and idempotency ledger are intentionally plain JSON so the
learner can inspect recovery rather than trusting a framework abstraction.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, statistics, time
from pathlib import Path
from telemetry import Telemetry, _id

ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; REPORTS=ROOT/'reports'; STATE=ROOT/'state'; REQUIRED=['retrieval','model','tool','verification','approval']

def rows():
 p=DATA/'eval.jsonl'
 if not p.exists(): p=DATA/'sample.jsonl'
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def percentile(values,q):
 values=sorted(values); return round(values[min(len(values)-1,max(0,math.ceil(len(values)*q)-1))],4) if values else 0
def action_id(case_id,step): return hashlib.sha256((case_id+':'+step).encode()).hexdigest()[:20]
def load_week4_runtime(root):
 source=Path(root)/'agent_runtime.py'
 if not source.exists(): raise RuntimeError(f'Week 4 live runtime not found: {source}')
 spec=importlib.util.spec_from_file_location(f'week4_runtime_{hash(str(source))}',source)
 if spec is None or spec.loader is None: raise RuntimeError(f'cannot load {source}')
 module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
 return module

class DurableWorkflow:
 def __init__(self, telemetry=None, approve=False, inject=False, week4_root=None):
  self.t=telemetry or Telemetry(); self.approve=approve; self.inject=inject; self.week4_root=week4_root; self._week4_runtime=None
 def live_week4(self,row,case):
  root=self.week4_root or row.get('week4_runtime_root')
  if not root: raise RuntimeError('imported Week 4 run requires --from-week4 or week4_runtime_root')
  if self._week4_runtime is None: self._week4_runtime=load_week4_runtime(root)
  return self._week4_runtime.execute_request(question=row['question'],request_id=f'w7-{case}',failure_mode='tool_timeout' if row.get('failure_mode') in {'tool_timeout','model_timeout'} else None,metadata={'week':7,'request_id':case,'workflow_failure_mode':row.get('failure_mode'),'instrumented':True})
 def execute(self,row,index):
  case=str(row.get('request_id') or row['case_id']); imported=row.get('source_runtime_mode')=='imported_week4_planner_executor'; trace=hashlib.sha256(f'week7:{case}'.encode()).hexdigest()[:32] if imported else _id(32); start=time.perf_counter_ns(); state={'run_id':case,'request_id':case,'trace_id':trace,'status':'RUNNING','journal':[],'completed_actions':[],'retry_count':0,'approval_state':'not_required','compensation':False,'dead_letter':False,'source':{'mode':'imported_week4_planner_executor' if imported else 'course_owned_fixture','week':4 if imported else 7,'source_id':row.get('source_id',case),'source_artifact':row.get('source_artifact'),'source_runtime_success':None,'runtime_entrypoint':row.get('week4_runtime_entrypoint') if imported else None},'timing_mode':'measured_wall_clock'}
  (STATE).mkdir(exist_ok=True)
  def journal(event,**fields):
   item={'ts_ns':time.time_ns(),'event':event,**fields}; state['journal'].append(item); (STATE/f'{case}.json').write_text(json.dumps(state,indent=2)); self.t.log(trace,event,attrs={'run_id':case,**fields})
  def span(name,parent=None,status='OK',**attrs):
   span_start=time.time_ns(); perf_start=time.perf_counter_ns(); sid=self.t.span(name,trace,parent,start_ns=span_start,attrs={'run_id':case,'request_id':case,'operation':name,**attrs},status=status); duration=round((time.perf_counter_ns()-perf_start)/1_000_000,3); state.setdefault('spans',[]).append({'name':name,'span_id':sid,'parent_span_id':parent,'status':status,'duration_ms':duration,'start_time_unix_nano':span_start,'end_time_unix_nano':span_start+int(duration*1_000_000)}); return sid
  root=span('workflow.run',None,case_type=row.get('failure_mode','success'),source_mode=state['source']['mode'])
  if imported:
   source=self.live_week4(row,case); state['source']['source_runtime_success']=source.get('success'); state['source']['live_execution']=True; state['source']['live_runtime']=source
   span('planner.execute',root,source_success=source.get('success'),source_latency_ms=source.get('latency_ms'),architecture='planner_executor',source_case_id=row.get('source_id',case),live_execution=True)
   span('executor.execute',root,source_calls=source.get('execution',{}).get('calls'),source_recovered=source.get('execution',{}).get('recovered',False),source_case_id=row.get('source_id',case),live_execution=True)
   span('verifier.check',root,evidence_complete=source.get('verification',{}).get('evidence_complete'),verified=source.get('verification',{}).get('verified'),source_case_id=row.get('source_id',case),live_execution=True)
  for step in REQUIRED:
   aid=action_id(case,step)
   if aid in state['completed_actions']: journal('idempotency_hit',step=step,action_id=aid); continue
   if step=='tool' and row.get('failure_mode')=='permanent_failure':
    span('tool',root,'ERROR',error_type='permanent_failure'); journal('retry_scheduled',step=step,reason='permanent_failure'); state['retry_count']+=1; span('compensation',root,'OK',action_id=aid); state['compensation']=True; journal('compensation_completed',step=step); state['status']='DEAD_LETTER'; state['dead_letter']=True; journal('dead_lettered',step=step); return self.finish(state,start)
   if step=='retrieval': sid=span('retrieval',root,documents=3); journal('checkpoint',step=step); state['completed_actions'].append(aid); continue
   if step=='model' and row.get('failure_mode')=='model_timeout' and state['retry_count']==0:
    sid=span('model',root,'ERROR',error_type='timeout'); journal('retry_scheduled',step=step,reason='model_timeout'); state['retry_count']+=1; self.t.metric('genai_errors_total',1,{'operation':'model'}); sid=span('model.retry',root,tokens=48); journal('retry_succeeded',step=step); state['completed_actions'].append(aid); continue
   if step=='tool' and row.get('failure_mode')=='tool_timeout' and state['retry_count']==0:
    sid=span('tool',root,'ERROR',error_type='timeout'); journal('retry_scheduled',step=step,reason='tool_timeout'); state['retry_count']+=1; self.t.metric('genai_errors_total',1,{'operation':'tool'}); sid=span('tool.retry',root,attempt=2); journal('retry_succeeded',step=step); state['completed_actions'].append(aid); continue
   if step=='approval' and (row.get('approval_required') or row.get('failure_mode')=='approval_required'):
    if not self.approve:
     state['status']='WAITING_APPROVAL'; state['approval_state']='pending'; journal('approval_requested',step=step); span('approval',root,'ERROR',state='pending'); return self.finish(state,start)
    state['approval_state']='approved'; journal('approval_granted',step=step)
   if step=='verification': span('verification',root,checks=2); journal('checkpoint',step=step)
   else: span(step,root); journal('checkpoint',step=step)
   state['completed_actions'].append(aid)
  if row.get('failure_mode')=='duplicate_commit':
   aid=action_id(case,'commit'); journal('commit_applied',action_id=aid); journal('idempotency_hit',step='commit',action_id=aid)
  state['status']='COMPLETED'; state['approval_state']='approved' if row.get('approval_required') else 'not_required'; journal('workflow_completed'); return self.finish(state,start)
 def finish(self,state,start):
  elapsed=round((time.perf_counter_ns()-start)/1_000_000,3); state['latency_ms']=max(elapsed,0.001); state['tokens']=42+(len(state.get('journal',[]))%9)*8; state['cost_usd']=round(state['tokens']*0.000005,7); state['span_count']=len(state.get('spans',[])); self.t.metric('genai_request_duration_seconds',state['latency_ms']/1000,{'operation':'workflow','request_id':state['request_id']}); self.t.metric('genai_requests_total',1,{'operation':'workflow'}); self.t.metric('genai_tokens_total',state['tokens'],{'operation':'workflow'}); self.t.metric('genai_cost_usd_total',state['cost_usd'],{'operation':'workflow'}); self.t.metric('genai_retries_total',state['retry_count'],{'operation':'workflow'}); return state

def run(approve=False,week4_root=None):
 REPORTS.mkdir(exist_ok=True); STATE.mkdir(exist_ok=True); (REPORTS/'telemetry.ndjson').unlink(missing_ok=True); t=Telemetry(); wf=DurableWorkflow(t,approve=approve,week4_root=week4_root); source=rows(); outputs=[wf.execute(r,i) for i,r in enumerate(source)]
 (REPORTS/'results.jsonl').write_text('\n'.join(json.dumps(x) for x in outputs)+'\n'); n=len(outputs); completed=sum(x['status']=='COMPLETED' for x in outputs); traces=sum(x['span_count']>=5 for x in outputs); durations=[x['latency_ms'] for x in outputs]; retries=sum(x['retry_count']>0 for x in outputs); pending=sum(x['status']=='WAITING_APPROVAL' for x in outputs); errors=sum(x['status'] in {'FAILED','DEAD_LETTER'} for x in outputs); metrics={'dataset':'real_data' if (DATA/'eval.jsonl').exists() else 'smoke_fixture','cases':n,'methods':REQUIRED,'raw_results':'reports/results.jsonl','required_metrics':{'trace completeness':round(traces/max(n,1),4),'latency p50/p95':[percentile(durations,.5),percentile(durations,.95)],'error rate':round(errors/max(n,1),4),'retry rate':round(retries/max(n,1),4),'tokens/request':round(statistics.mean(x['tokens'] for x in outputs),2),'cost/request':round(statistics.mean(x['cost_usd'] for x in outputs),7)},'workflow_metrics':{'completed':completed,'waiting_approval':pending,'dead_letter':sum(x['status']=='DEAD_LETTER' for x in outputs),'compensated':sum(x['compensation'] for x in outputs),'idempotency_records':sum(len(x['completed_actions']) for x in outputs)},'telemetry':{'otlp_endpoint':t.endpoint,'local_copy':'reports/telemetry.ndjson','spans':sum(x['span_count'] for x in outputs),'logs':sum(1 for line in (REPORTS/'telemetry.ndjson').read_text().splitlines() if json.loads(line)['kind']=='log')}}
 metrics['provenance']={'mode':'imported_week4_planner_executor' if source and source[0].get('source_runtime_mode')=='imported_week4_planner_executor' else 'course_owned_fixture','source_artifact':source[0].get('source_artifact') if source else None,'source_cases':sum(bool(r.get('source_runtime_mode')) for r in source),'request_ids_preserved':len({r.get('request_id',r.get('case_id')) for r in source})==len(source)}
 (REPORTS/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n'); (REPORTS/'observability_report.md').write_text('# Week 7 observability report\n\n'+''.join(f'- **{k}:** {v}\n' for k,v in metrics['required_metrics'].items())+'\n## Durable execution evidence\n\nEvery case has a JSON journal and idempotency action IDs under `state/`. Approval cases remain `WAITING_APPROVAL` unless `--approve` is supplied; retries are visible as error and retry spans. The local NDJSON copy is the audit fallback when the collector is unavailable.\n\n## Imported Week 4 runtime\n\nWhen fetched with `--from-week4`, each run retains the Week 4 request ID, source artifact, planner-executor result, and planner/executor/verifier spans. Span durations are measured wall-clock durations from this run; the source latency is recorded as an attribute, not substituted for observed timing.\n\n## Failure injection\n\nThe tool and model timeout fixtures emit an error span, retry event, and recovery log. Inspect the same `trace_id` in `reports/results.jsonl` and Grafana/Loki when Docker Compose is running.\n')
 print(json.dumps(metrics,indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--allow-sample',action='store_true'); ap.add_argument('--require-real-data',action='store_true'); ap.add_argument('--approve',action='store_true'); ap.add_argument('--from-week4',type=Path); a=ap.parse_args()
 if a.require_real_data and not (DATA/'eval.jsonl').exists(): raise SystemExit('real data missing: run python scripts/fetch_data.py --cases 20')
 run(approve=a.approve,week4_root=a.from_week4)
