"""Fetch BANKING77 without hiding offline fallback provenance."""
from __future__ import annotations
import csv, hashlib, json, pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
URL = "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/{split}.csv"

def sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def fetch_split(split):
    target=DATA/f"{split}.jsonl"
    try:
        raw=urllib.request.urlopen(URL.format(split=split), timeout=20).read()
        rows=[]
        for i,r in enumerate(csv.DictReader(raw.decode("utf-8").splitlines())):
            text=(r.get("text") or r.get("sentence") or "").strip(); label=(r.get("category") or r.get("label") or "").strip()
            if text and label: rows.append({"id":f"banking77-{split}-{i:05d}","text":text,"label":label,"split":split})
        if len(rows)<20: raise ValueError("download contained too few labelled rows")
        target.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in rows)+"\n")
        return "public_download", len(rows)
    except Exception as exc:
        # Keep the smoke fixture runnable, but record that it is not a benchmark run.
        if split == "train":
            source=[json.loads(x) for x in (DATA/"sample.jsonl").read_text().splitlines()]
            rows=[]
            for i,r in enumerate(source): rows.append({**r,"id":f"fixture-train-{i:03d}","split":"train"})
            target.write_text("\n".join(json.dumps(x) for x in rows)+"\n")
            return "offline_fixture", len(rows)
        # A test fixture is deliberately disjoint in IDs and text.
        source=[json.loads(x) for x in (DATA/"sample.jsonl").read_text().splitlines()]
        rows=[{**r,"id":f"fixture-test-{i:03d}","text":r["text"]+" (test wording)","split":"test"} for i,r in enumerate(reversed(source))]
        target.write_text("\n".join(json.dumps(x) for x in rows)+"\n")
        return "offline_fixture", len(rows)

def main():
    sources={}; counts={}
    for split in ("train","test"):
        sources[split],counts[split]=fetch_split(split)
    # The published BANKING77 files contain a few duplicated utterances across
    # splits. Remove those test rows so evaluation remains uncontaminated.
    train_rows=[json.loads(x) for x in (DATA/"train.jsonl").read_text().splitlines() if x.strip()]
    test_rows=[json.loads(x) for x in (DATA/"test.jsonl").read_text().splitlines() if x.strip()]
    norm=lambda s:" ".join(sorted(set(re.findall(r"[a-z0-9]+",s.lower()))))
    train_text={norm(x["text"]) for x in train_rows}
    clean_test=[x for x in test_rows if norm(x["text"]) not in train_text]
    (DATA/"test.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in clean_test)+"\n")
    counts["test"]=len(clean_test)
    m=json.loads((DATA/"manifest.json").read_text())
    m["source_type"]="public_download" if all(x=="public_download" for x in sources.values()) else "offline_fixture"
    m["counts"]=counts; m["sha256"]={s:sha(DATA/f"{s}.jsonl") for s in ("train","test")}; m["fetch_error"] = None if m["source_type"]=="public_download" else "network unavailable or source rejected; use public download for benchmark claims"
    (DATA/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(json.dumps({"source_type":m["source_type"],"counts":counts,"manifest":"data/manifest.json"}))
if __name__=="__main__": main()
