"""Fetch and normalize a pinned QASPER split without duplicating records."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
URL = "https://datasets-server.huggingface.co/rows?dataset=allenai/qasper&config=qasper&split=train&offset={offset}&length={length}"
def download(url):
    request = urllib.request.Request(url, headers={"User-Agent":"advanced-ai-systems-course/2.0"})
    with urllib.request.urlopen(request, timeout=45) as response: return response.read()
def flatten_sections(paper):
    docs=[]
    full=paper.get("full_text", [])
    if isinstance(full,dict):
        names=full.get("section_name", []); paragraphs=full.get("paragraphs", [])
        full=[{"section_name": names[i] if i < len(names) else f"section-{i+1}", "paragraphs": paragraphs[i] if i < len(paragraphs) else []} for i in range(len(paragraphs))]
    for section_index, section in enumerate(full):
        if not isinstance(section,dict): continue
        name = section.get("section_name") or f"section-{section_index+1}"
        for paragraph_index, text in enumerate(section.get("paragraphs", [])):
            if text and str(text).strip(): docs.append({"id":f"{paper.get('id','paper')}:{section_index}:{paragraph_index}","title":paper.get("title", ""),"section":name,"text":str(text)})
    return docs
def answer_text(answers):
    if not answers: return ""
    if isinstance(answers,dict): answers=answers.get("answer", answers)
    item=answers[0] if isinstance(answers,list) else answers
    if isinstance(item,list): item=item[0] if item else {}
    if isinstance(item,dict): return str(item.get("answer") or item.get("free_form_answer") or item.get("extractive_spans") or "")
    return str(item)
def evidence_id(paper, qa, docs):
    answers=qa.get("answers") or []
    if isinstance(answers,dict): answers=answers.get("answer", answers)
    if answers and isinstance(answers[0],list): answers=answers[0]
    evidence=[]
    if answers and isinstance(answers[0],dict): evidence=answers[0].get("evidence") or []
    # QASPER evidence can be paragraph indices or source snippets.  A record
    # without resolvable source evidence is not an evaluation example: choosing
    # the first paragraph would make Recall@5 a fabricated target.
    def flatten(items):
        for item in items if isinstance(items, list) else [items]:
            if isinstance(item, list):
                yield from flatten(item)
            else:
                yield item
    for item in flatten(evidence):
        if isinstance(item, int) and 0 <= item < len(docs): return docs[item]["id"]
        if isinstance(item, str):
            needle=" ".join(item.lower().split())
            for d in docs:
                haystack=" ".join(d["text"].lower().split())
                if needle and (needle in haystack or haystack in needle): return d["id"]
    return None
def normalize(raw, limit):
    if isinstance(raw,dict) and raw.get("rows"):
        papers = [item.get("row", item) for item in raw["rows"]]
    else:
        papers = raw.values() if isinstance(raw,dict) else raw
    rows=[]
    for paper in papers:
        docs=flatten_sections(paper)
        qas=paper.get("qas", paper.get("qa", []))
        if isinstance(qas,dict):
            questions=qas.get("question",[]); qids=qas.get("question_id",[]); answers=qas.get("answers",[])
            qas=[{"question":questions[i] if i<len(questions) else "", "question_id":qids[i] if i<len(qids) else "", "answers":answers[i] if i<len(answers) else []} for i in range(len(questions))]
        for qa in qas:
            question=qa.get("question","").strip()
            if not question or not docs: continue
            gold=evidence_id(paper,qa,docs)
            if not gold: continue
            rows.append({"case_id":f"week-2-{len(rows)+1:04d}","question_id":str(qa.get("question_id") or qa.get("id") or len(rows)),"question":question,"answer":answer_text(qa.get("answers")),"evidence_id":gold,"documents":docs,"source_record":paper.get("id","qasper"),"source_title":paper.get("title","")})
            if len(rows)>=limit: return rows
    return rows
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cases",type=int,default=200); ap.add_argument("--url",default=URL); args=ap.parse_args()
    try:
        pages=[]
        for offset in range(0,args.cases,100):
            count=min(100,args.cases-offset)
            url=args.url.format(offset=offset,length=count) if "{offset}" in args.url else args.url
            page=json.loads(download(url)); pages.extend(page.get("rows", []))
            if "{offset}" not in args.url: break
        raw_obj={"rows":pages,"num_rows_total":len(pages)}; raw=json.dumps(raw_obj).encode()
    except Exception as exc: raise SystemExit(f"QASPER download failed; no synthetic fallback is allowed: {exc}")
    (ROOT/"data/source.download").write_bytes(raw)
    rows=normalize(raw_obj,args.cases)
    if len(rows)<args.cases: raise SystemExit(f"QASPER produced only {len(rows)} usable unique questions; requested {args.cases}")
    payload="".join(json.dumps(x,sort_keys=True)+"\n" for x in rows); (ROOT/"data/eval.jsonl").write_text(payload)
    digest=hashlib.sha256(payload.encode()).hexdigest()
    (ROOT/"data/manifest.json").write_text(json.dumps({"status":"real_data","dataset":"QASPER train","source":args.url,"cases":len(rows),"unique_case_ids":len({r['case_id'] for r in rows}),"unique_source_records":len({r['source_record'] for r in rows}),"sha256":digest,"source_download_sha256":hashlib.sha256(raw).hexdigest(),"provenance":"QASPER public download; question and evidence IDs preserved; no row repetition","generated_by":"scripts/fetch_data.py"},indent=2)+"\n")
    print(f"Wrote {len(rows)} unique QASPER questions; manifest sha256={digest}")
if __name__=="__main__": main()
