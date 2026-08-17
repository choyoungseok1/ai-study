import json, os, arxiv

d = json.load(open(os.path.join("data", "arxiv", "candidates.json"), encoding="utf-8"))
KEY = ("Dissecting Agentic", "Ideal Evidence")
for r in d:
    if any(k in r["title"] for k in KEY):
        print("[" + r["arxiv_id"] + "] " + r["title"])
        print(r["abstract"][:900])
        print("-" * 70)

print("\n=== Adaptive-RAG 원 논문 재검색 ===")
c = arxiv.Client()
q = 'ti:"Learning to Adapt Retrieval-Augmented Large Language Models"'
for r in c.results(arxiv.Search(query=q, max_results=3)):
    print(r.entry_id.rsplit("/", 1)[-1], r.title)
