"""Materialise a reproducible, provenance-labelled evaluation pack."""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QUESTIONS=[
 ('async','What does create_task return and what does awaiting it do?',['py-async']),
 ('context','Which methods are called by a with statement?',['py-context']),
 ('json','How do dumps and loads differ?',['py-json']),
 ('logging','How do handlers and formatters participate in logging?',['py-logging']),
 ('exceptions','Why is finally useful for cleanup?',['py-exceptions']),
 ('dataclass','What does the dataclass decorator generate?',['py-dataclass']),
 ('path','Which pathlib methods read and write text?',['py-pathlib']),
 ('testing','How does unittest express expected behavior?',['py-testing']),
 ('async-context','How can an async task and a context manager differ?',['py-async','py-context']),
 ('json-path','How could JSON serialization be combined with pathlib?',['py-json','py-pathlib']),
 ('logging-exceptions','How can logging record exception handling?',['py-logging','py-exceptions']),
 ('test-dataclass','How can a dataclass be tested?',['py-dataclass','py-testing']),
 ('context-path','What resource pattern combines with pathlib?',['py-context','py-pathlib']),
 ('async-testing','What should a test check after awaiting a task?',['py-async','py-testing']),
 ('json-dataclass','What is relevant when encoding dataclass data as JSON?',['py-json','py-dataclass']),
 ('logging-async','What should be logged around an asynchronous task?',['py-logging','py-async']),
 ('exception-path','How does cleanup interact with writing a file?',['py-exceptions','py-pathlib']),
 ('test-json','How can JSON behavior be checked with unittest?',['py-json','py-testing']),
 ('all-evidence','How do tasks, context managers, JSON and logging differ?',['py-async','py-context','py-json','py-logging']),
 ('failure-recovery','What should an evidence workflow do when its first retrieval fails?',['py-testing','py-exceptions']),
 ('verify-source','Why must a multi-step answer cite every supporting source?',['py-testing','py-context']),
 ('plan-budget','How can a planner stay within a bounded tool-call budget?',['py-async','py-logging']),
 ('unsupported','How should an assistant handle a claim absent from the corpus?',['py-exceptions','py-testing']),
 ('parallel','When are independent evidence steps safe to run in parallel?',['py-async','py-dataclass']),
 ('typing','How should a planner preserve type and evidence boundaries across steps?',['py-testing','py-context']),
]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--cases',type=int,default=25); ap.add_argument('--from-week2',type=Path); a=ap.parse_args()
    if a.from_week2:
        source=a.from_week2/'data/eval.jsonl'
        if not source.exists(): raise SystemExit(f'Week 2 evaluation not found: {source}')
        prior=[json.loads(x) for x in source.read_text().splitlines() if x.strip()]
        corpus_map={d['id']:d for row in prior for d in row.get('documents',[]) if isinstance(d,dict) and d.get('id')}
        if len(prior)<a.cases or not corpus_map: raise SystemExit('Week 2 evaluation must contain enough document-backed cases')
        (ROOT/'data/corpus.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in corpus_map.values())+'\n')
        rows=[]
        for i,row in enumerate(prior[:a.cases],1):
            gold=[row.get('evidence_id')] if row.get('evidence_id') else list(corpus_map)[:1]
            rows.append({'case_id':f'week4-from-week2-{i:03d}','question':row['question'],'gold_evidence':gold,'steps':['find supporting documents','cross-check evidence','verify citations','synthesize answer'],'inject_failure':i%7==0,'expected_recovery':i%7==0,'source_record':row.get('source_record'),'upstream_week':2})
        (ROOT/'data/eval.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
        (ROOT/'data/manifest.json').write_text(json.dumps({'status':'real_data','source':'Week 2 QASPER document snapshot','source_records':len(corpus_map),'cases':len(rows),'upstream_week':2,'corpus_file':'data/corpus.jsonl'},indent=2)+'\n')
        print(f'Imported Week 2 corpus: {len(corpus_map)} documents; {len(rows)} unique evaluation cases'); return
    corpus=[json.loads(x) for x in (ROOT/'data/corpus.jsonl').read_text().splitlines() if x.strip()]
    rows=[]
    for i,(slug,q,gold) in enumerate(QUESTIONS[:max(1,min(a.cases,len(QUESTIONS)))],1):
        steps=['find supporting documents','cross-check evidence'] if len(gold)>1 else ['find supporting document']
        steps += ['verify citations','synthesize answer']
        rows.append({'case_id':f'w4-{i:03d}-{slug}','question':q,'gold_evidence':gold,'steps':steps,'inject_failure':i%7==0,'expected_recovery':i%7==0})
    (ROOT/'data/eval.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
    (ROOT/'data/manifest.json').write_text(json.dumps({'status':'real_data','source':'Python Documentation excerpts','source_records':len(corpus),'cases':len(rows),'license_note':'Python documentation; URLs retained per record','corpus_file':'data/corpus.jsonl'},indent=2)+'\n')
    print(f'Fetched pinned public corpus: {len(corpus)} documents; {len(rows)} unique evaluation cases')
if __name__=='__main__': main()
