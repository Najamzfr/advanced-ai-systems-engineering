"""Reference bounded agent: every tool action goes through MCP JSON-RPC."""
import argparse, json, math, subprocess, time, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load():
 p=ROOT/'data/eval.jsonl'; p=p if p.exists() else ROOT/'data/sample.jsonl'
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]

class MCPClient:
 def __init__(self):
  self.proc=subprocess.Popen(['python','mcp_server.py'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1); self.seq=0; self.calls=[]
  self.request('initialize',{}); self.tools=self.request('tools/list',{})['tools']; self.tool_schemas={tool['name']:tool.get('inputSchema',{}) for tool in self.tools}
 def request(self,method,params):
  self.seq+=1; req={'jsonrpc':'2.0','id':self.seq,'method':method,'params':params}; self.proc.stdin.write(json.dumps(req)+'\n'); self.proc.stdin.flush(); out=json.loads(self.proc.stdout.readline())
  if out.get('error'): raise RuntimeError(out['error']['message'])
  return out['result']
 def call(self,name,args,retries=1):
  if name not in self.tool_schemas: raise ValueError(f'{name} was not advertised by the MCP server')
  schema=self.tool_schemas[name]
  missing=[field for field in schema.get('required',[]) if field not in args]
  if missing: raise ValueError(f'{name} is missing required arguments: {", ".join(missing)}')
  expected={field:meta.get('type') for field,meta in schema.get('properties',{}).items()}
  type_ok={'string':str,'object':dict,'boolean':bool}
  wrong=[field for field,value in args.items() if expected.get(field) in type_ok and not isinstance(value,type_ok[expected[field]])]
  if wrong: raise ValueError(f'{name} has invalid argument types: {", ".join(wrong)}')
  started=time.perf_counter()
  for attempt in range(1,retries+2):
   try:
    result=self.request('tools/call',{'name':name,'arguments':args}); payload=json.loads(result['content'][0]['text']); self.calls.append({'tool':name,'arguments':args,'valid':True,'attempt':attempt,'duration_ms':round((time.perf_counter()-started)*1000,3),'transport':'mcp-json-rpc'}); return payload
   except Exception as exc:
    self.calls.append({'tool':name,'arguments':args,'valid':False,'attempt':attempt,'error':str(exc)})
    if attempt>retries: raise
  raise RuntimeError('unreachable')
 def close(self):
  if self.proc.poll() is None: self.proc.terminate(); self.proc.wait(timeout=2)

def run(row, inject_transient_failure=False):
 c=MCPClient(); q=row['question']; action='store:'+hashlib.sha256(row['case_id'].encode()).hexdigest()[:16]; trajectory=[]
 try:
  search=c.call('search_documents',{'query':q}); trajectory.append(c.calls[-1]); hits=search['records']; selected=hits[0]['evidence_id'] if hits else ''
  fetched=c.call('fetch_document',{'id':selected}); trajectory.append(c.calls[-1]); record=fetched['record']
  value={'location':record['location'],'temperature':record.get('temperature_2m'),'wind_speed':record.get('wind_speed_10m'),'evidence_id':record['evidence_id']}
  store_args={'action_id':action,'case_id':row['case_id'],'value':value}
  if inject_transient_failure: store_args['simulate_transient_failure']=True
  stored=c.call('store_result',store_args); trajectory.append(c.calls[-1])
  duplicate=c.call('store_result',store_args); trajectory.append(c.calls[-1])
  return {'case_id':row['case_id'],'expected_tool':row.get('expected_tool','search_documents'),'trajectory':trajectory,'selected_evidence_id':selected,'completed':bool(record and stored.get('stored') is True),'duplicate_effect':duplicate.get('duplicate') is False,'server_round_trip':True,'discovered_tools':sorted(c.tool_schemas),'retry_count':sum(x.get('attempt',1)-1 for x in trajectory),'answer':value}
 finally: c.close()

def percentile(xs,q):
 xs=sorted(xs); return round(xs[min(len(xs)-1,max(0,math.ceil(len(xs)*q)-1))],3) if xs else 0
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--allow-sample',action='store_true'); ap.add_argument('--require-real-data',action='store_true'); ap.add_argument('--inject-one-failure',action='store_true',help='inject one explicit transient MCP store failure to verify retry + idempotency'); a=ap.parse_args(); manifest=json.loads((ROOT/'data/manifest.json').read_text())
 if a.require_real_data and manifest.get('status')!='real_data': raise SystemExit('real data required: run scripts/fetch_data.py --cases 20')
 rows=load(); results=[run(r, inject_transient_failure=a.inject_one_failure and index==0) for index,r in enumerate(rows)]; n=len(results); valid=sum(all(x['valid'] for x in r['trajectory']) for r in results); complete=sum(r['completed'] for r in results); duplicates=sum(r['duplicate_effect'] for r in results); retries=sum(r['retry_count']>0 for r in results)
 metrics={'dataset':manifest.get('status'),'cases':n,'raw_results':'reports/results.jsonl','methods':['search_documents','fetch_document','store_result'],'required_metrics':{'tool-selection accuracy':round(sum(r['trajectory'][0]['tool']==r['expected_tool'] for r in results)/n,4),'argument validity':round(valid/n,4),'successful completion rate':round(complete/n,4),'retry rate':round(retries/n,4),'duplicate-effect rate':round(duplicates/n,4)},'trajectory_denominator':n,'server_calls':sum(len(r['trajectory']) for r in results),'latency p95 ms':percentile([sum(x.get('duration_ms',0) for x in r['trajectory']) for r in results],.95),'idempotency_checks':n,'failure_injection':{'enabled':a.inject_one_failure,'injected_cases':sum(r['retry_count']>0 for r in results)}}
 out=ROOT/'reports'; out.mkdir(exist_ok=True); (out/'results.jsonl').write_text('\n'.join(json.dumps(r) for r in results)+'\n'); (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n'); (out/'agent_decision.md').write_text('# Week 3 measured report\n\nThe agent discovered and called the MCP-compatible server; no tool result is assembled without a server response.\n\n'+'\n'.join(f'- {k}: {v}' for k,v in metrics['required_metrics'].items())+f"\n\nCases: {n}; MCP calls: {metrics['server_calls']}; latency p95: {metrics['latency p95 ms']} ms.\n\nBoundary: the offline agent has a fixed tool budget and does not claim model-provider quality; replace deterministic routing only after preserving these contracts.\n")
 print(json.dumps(metrics,indent=2))
if __name__=='__main__': main()
