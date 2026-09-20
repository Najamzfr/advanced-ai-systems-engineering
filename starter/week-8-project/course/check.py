"""Evidence-derived Week 8 checker. It never trusts a learner-provided pass flag."""
from __future__ import annotations
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; REPORTS=ROOT/'reports'
def load(name):
    p=REPORTS/name
    if not p.exists(): raise AssertionError(f'missing {p}')
    return json.loads(p.read_text())
def check(step):
    if step==1:
        for p in ('Dockerfile','docker-compose.yml','serve.py','RELEASE.md','integration/deployment-contract.json'): assert (ROOT/p).exists(),f'missing {p}'
        print('PASS: release contract and smoke stack are ready'); return
    metrics=load('metrics.json'); report=load('release_report.json')
    if step==2:
        assert metrics.get('cases',0)>0,'metrics cases missing'; assert metrics.get('execution',{}).get('mode') in ('smoke_fixture','live_coursework'),'execution mode missing'; print('PASS: release metrics are present and labelled'); return
    if step==3:
        manifest=json.loads((DATA/'manifest.json').read_text()); assert manifest.get('status')=='materialized','materialized manifest required'; assert metrics['cases']>=150,'need 150 release cases'; assert report['checks']['evaluation_cases']==metrics['cases'],'case denominator mismatch'; print(f"PASS: release case count and manifest are valid ({metrics['cases']})"); return
    if step==4:
        assert (REPORTS/'results.jsonl').exists(),'raw release results missing'; rows=[json.loads(x) for x in (REPORTS/'results.jsonl').read_text().splitlines() if x.strip()]; assert len(rows)==metrics['cases'],'raw/result denominator mismatch'; print('PASS: raw release evidence matches metrics denominator'); return
    if step==5:
        assert set(metrics['failure_matrix'])=={'model_unavailable','retrieval_down','tool_timeout','database_timeout','approval_timeout'},'failure matrix incomplete'; assert metrics['observability']['trace_count']==metrics['cases'],'trace denominator mismatch'; assert 'latency_p95_ms' in metrics and 'cost_per_successful_task' in metrics,'SLO metrics missing'; print('PASS: failure matrix, traces and SLO fields are present'); return
    if step==6:
        assert all(isinstance(x.get('recovery_success_rate'),(int,float)) for x in metrics['failure_matrix'].values()),'recovery metrics missing'; print('PASS: recovery rates are numeric and derived'); return
    if step==7:
        assert metrics['observability']['trace_count']==metrics['cases'],'trace count mismatch'; print('PASS: one trace is recorded per release case'); return
    if step==8:
        assert all(k in metrics['slo'] for k in ('latency_pass','cost_pass')),'SLO decisions missing'; print('PASS: latency and cost SLO decisions are present'); return
    if step==9:
        rows=[json.loads(x) for x in (REPORTS/'results.jsonl').read_text().splitlines() if x.strip()]
        assert all('failure' in x and 'trace_id' in x for x in rows),'raw trace fields missing'
        if metrics.get('execution',{}).get('mode')=='live_coursework':
            required={'retrieval','mcp','agent','security','adaptation','workflow'}
            assert all(x.get('execution_mode')=='live_coursework' and required.issubset(x.get('components',{})) for x in rows),'release rows did not execute all six live components'
            assert all(x['components']['agent'].get('runtime',{}).get('live_execution') for x in rows),'Week 4 agent runtime was not live'
            assert all(x['components']['mcp'].get('server_round_trip') for x in rows),'Week 3 MCP runtime was not live'
            assert all(x['components']['adaptation'].get('live_execution') and x['components']['adaptation'].get('real_lora_complete') for x in rows),'Week 6 real LoRA runtime was not live'
            assert all(x['components']['workflow'].get('trace_id')==x['trace_id'] for x in rows),'Week 7 trace provenance mismatch'
        print('PASS: raw rows include trace and live-component evidence'); return
    if step==10:
        assert (ROOT/'monitoring/dashboard.json').exists(),'dashboard export missing'; print('PASS: dashboard export is present'); return
    if step==11:
        upstream=json.loads((ROOT/'integration/upstream-contract.json').read_text()); assert len(upstream['consumes'])==7,'Weeks 1-7 integration contract incomplete'; evidence=json.loads((DATA/'upstream-evidence.json').read_text()); weeks=evidence.get('weeks',[]); assert len(weeks)==7,'real upstream evidence missing; fetch with --upstream-root'; assert {x.get('domain') for x in weeks}=={'evaluation','retrieval','tools','planning','security','adaptation','observability'},'domain evidence is incomplete'; assert all(x.get('raw_case_count',0)>0 and x.get('artifacts') for x in weeks),'raw upstream artifacts missing'; assert metrics.get('upstream_execution',{}).get('rows_materialized',0)==metrics['cases'],'release rows were not materialized from upstream'; assert metrics.get('execution',{}).get('mode')=='live_coursework','promotion requires live component execution'; print('PASS: upstream contract, raw artifacts and seven live prior-week domains are present'); return
    if step==12:
        assert report['release_pass'] is True,'release checks are not passing'; final=(REPORTS/'final_report.md').read_text(); assert 'Limits' in final and len(final)>250,'final defense is too thin'; print('PASS: final report and release decision are complete'); return
    raise AssertionError('unknown step')
def main():
    target=sys.argv[1] if len(sys.argv)>1 else 'grade'
    if target=='setup': print('PASS: release contract ready'); return
    if target=='grade':
        for i in range(1,13): check(i)
        print('GRADE PASS: Week 8 release evidence is complete'); return
    if target.startswith('check-step-'): check(int(target.rsplit('-',1)[1])); return
    raise SystemExit(f'unknown target: {target}')
if __name__=='__main__':
    try: main()
    except (AssertionError,FileNotFoundError,KeyError) as e: print(f'FAIL: {e}'); raise SystemExit(1)
