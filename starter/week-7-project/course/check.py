import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_CASES = 20
REQUIRED_METRICS = ["trace completeness","latency p50/p95","error rate","retry rate","tokens/request","cost/request"]

def evidence(passed, observed, required, message):
    return {"passed": bool(passed), "observed": observed, "required": required, "message": message}

def setup():
    required = [ROOT/'data/manifest.json', ROOT/'data/sample.jsonl', ROOT/'project.py', ROOT/'reports']
    missing = [str(x.relative_to(ROOT)) for x in required if not x.exists()]
    if missing: raise SystemExit('Missing starter paths: ' + ', '.join(missing))
    print('setup: ready; smoke fixture available; real benchmark not claimed')

def load_state():
    manifest_path=ROOT/'data/manifest.json'; metrics_path=ROOT/'reports/metrics.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    metrics=json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    return manifest, metrics

def checks():
    manifest, metrics = load_state()
    artifact = ROOT/'reports/observability_report.md'
    report_checks = {
        'smoke_metrics': evidence(metrics.get('dataset') in {'smoke_fixture','real_data'} and 'cases' in metrics, metrics.get('dataset', 'missing'), 'metrics.json with dataset and cases', 'run make run'),
        'real_data': evidence(manifest.get('status') == 'real_data', manifest.get('status', 'missing'), 'real_data', 'fetch the assigned real dataset'),
        'minimum_cases': evidence(manifest.get('cases', 0) >= MIN_CASES, manifest.get('cases', 0), f'>= {MIN_CASES}', 'meet the declared minimum case count'),
        'metrics_cases': evidence(metrics.get('cases', 0) >= MIN_CASES, metrics.get('cases', 0), f'>= {MIN_CASES}', 'run the real evaluation'),
        'required_metrics': evidence(set(metrics.get('required_metrics', {})) == set(REQUIRED_METRICS), sorted(metrics.get('required_metrics', {})), REQUIRED_METRICS, 'write every week-specific metric key'),
        'artifact': evidence(artifact.exists(), str(artifact.relative_to(ROOT)) if artifact.exists() else 'missing', str(artifact.relative_to(ROOT)), 'write the required report artifact'),
    }
    return report_checks

def grade():
    report_checks = checks()
    errors=[f'{name}: {item["message"]}' for name,item in report_checks.items() if not item['passed']]
    result={'status':'pass' if not errors else 'fail','summary':{'passed':sum(item['passed'] for item in report_checks.values()),'total':len(report_checks)},'checks':report_checks,'errors':errors}
    (ROOT/'reports/grade.json').write_text(json.dumps(result,indent=2)+'\n')
    if errors: raise SystemExit('GRADE FAIL\n- '+'\n- '.join(errors)+'\nMachine-readable result: reports/grade.json')
    print('GRADE PASS\n- real data\n- minimum case count\n- required metrics\n- required artifact\nMachine-readable result: reports/grade.json')

def check_step(step):
    if step < 1 or step > 12: raise SystemExit('step must be between 1 and 12')
    group=(step-1)//3
    report_checks=checks()
    if group == 0: names=['smoke_metrics']
    elif group == 1: names=['real_data','minimum_cases']
    elif group == 2: names=['required_metrics']
    else: names=['artifact']
    failures=[f'{name}: {report_checks[name]["message"]}' for name in names if not report_checks[name]['passed']]
    if failures:
        print('STEP FAIL')
        for failure in failures: print('- '+failure)
        raise SystemExit(1)
    print(f'STEP PASS {step}: '+', '.join(names))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['setup','grade']+[f'check-step-{n}' for n in range(1,13)]); args=parser.parse_args()
    if args.command=='setup': setup()
    elif args.command=='grade': grade()
    else: check_step(int(args.command.rsplit('-',1)[1]))
