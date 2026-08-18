# scripts/probe_html.py
import json, os, time, urllib.request

sel = json.load(open(os.path.join("data", "arxiv", "selected.json"), encoding="utf-8"))
ok, no = [], []
for r in sel:
    aid = r["arxiv_id"]
    url = f"https://arxiv.org/html/{aid}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "corpus-probe"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            (ok if resp.status == 200 else no).append((aid, r["published"][:4]))
    except Exception as e:
        no.append((aid, r["published"][:4]))
    time.sleep(1)          # ⚠️ arXiv 초당 3요청 제한

print(f"HTML 있음 {len(ok)} / 없음 {len(no)}\n")
for aid, y in no:
    print(f"  ❌ {aid:14} {y}")