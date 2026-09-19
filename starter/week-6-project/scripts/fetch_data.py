import argparse, json, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--cases',type=int,default=300); p.add_argument('--url',default='local:course-split-manifest.json'); a=p.parse_args()
    if a.url.startswith('http'):
        raw=urllib.request.urlopen(a.url,timeout=60).read()
        (ROOT/'data/source.bin').write_bytes(raw)
    else:
        raw=b'course-source-reference'
    print('Downloaded source bytes to data/source.bin. Implement the week-specific parser, write data/eval.jsonl, then update the manifest checksum before running make evaluate.')

if __name__=='__main__': main()
