"""
Phase B Step 2-2 — 코퍼스 내부 인용 그래프
2026-08-18 (Week 18)

⚠️ 왜 따로 만드나 — fetch_sources.py 가 인용을 0건으로 냈다

  원인 두 개:
  1. **`\\bibitem` 은 보통 `.bbl` 에 있다.** BibTeX 를 쓰면 본문에는
     `\\bibliography{refs}` 만 있고 실제 항목은 컴파일 산출물인 `.bbl` 에 생긴다.
     `read_tex_files` 가 `.tex` 만 읽어서 통째로 놓쳤다.
     → 40편 전부 0건인 게 우연이 아니라 구조적이었다는 신호였다.
  2. **arXiv ID 없이 학회명만 적는 항목이 많다.**
     "Asai et al. Self-RAG. ICLR 2024." 같은 식이라 ID 매칭만으로는 절반을 놓친다.
     → **제목 매칭**을 함께 쓴다. 코퍼스 40편의 제목이 남의 bib 에 나오는지 본다

★ 이 그래프가 Phase B Step 4(QA쌍 수작업)의 병목을 줄인다.
  "A 논문이 인용한 방법 B" 쌍이 자동으로 나오면 bridge 질문 재료를 찾아 헤맬 필요가 없다.

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.build_citations
      python -m scripts.build_citations --debug 2310.11511   # 한 편 진단
"""
import os
import re
import sys
import json
import gzip
import tarfile
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
ARXIV_DIR = os.path.join(_DATA, "arxiv")
SRC_DIR = os.path.join(ARXIV_DIR, "src")
SECTIONS = os.path.join(ARXIV_DIR, "sections.json")
OUT = os.path.join(ARXIV_DIR, "citations.json")

# bib 항목 경계. \bibitem 뿐 아니라 BibTeX 원본(@article{...})도 대비
_BIBITEM = re.compile(
    r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}(.*?)(?=\\bibitem|\\end\{thebibliography\}|\Z)",
    re.S)
_ARXIV_ID = re.compile(r"(?:arxiv[:\s./]*|abs/)(\d{4}\.\d{4,5})", re.I)

_TITLE_MIN = 28        # 제목 매칭에 쓸 최소 길이. 짧으면 오탐이 는다


def read_all_text(path):
    """압축 안에서 텍스트로 읽을 수 있는 건 전부.

    ⚠️ `.tex` 만 읽으면 `.bbl` 을 놓친다. 확장자를 넓힌다.
    """
    keep = (".tex", ".bbl", ".bib", ".ltx")
    out = {}
    try:
        with tarfile.open(path) as tf:
            for m in tf.getmembers():
                if m.isfile() and m.name.lower().endswith(keep):
                    out[m.name] = tf.extractfile(m).read().decode("utf-8", "replace")
        return out
    except tarfile.ReadError:
        pass
    try:
        with gzip.open(path, "rb") as f:
            raw = f.read()
        if raw[:4] != b"%PDF":
            return {"main.tex": raw.decode("utf-8", "replace")}
    except Exception:
        pass
    return {}


def norm_title(s):
    """제목 정규화 — 대소문자·구두점·공백 차이를 없앤다.

    ⚠️ 8/17 EM 정규화 교훈과 같은 발상: 문자를 나열하지 말고 범주로.
      여기서는 영숫자만 남긴다.
    """
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def entries_of(text):
    """(키, 항목 원문) 목록. \\bibitem 이 없으면 줄 단위로라도 쪼갠다."""
    items = [(k.strip(), v) for k, v in _BIBITEM.findall(text)]
    if items:
        return items
    # BibTeX 원본이 딸려온 경우
    chunks = re.split(r"(?=@\w+\s*\{)", text)
    return [(f"bib{i}", c) for i, c in enumerate(chunks) if len(c) > 40]


def main():
    papers = json.load(open(SECTIONS, encoding="utf-8"))
    corpus_ids = {p["arxiv_id"] for p in papers}
    # 제목 → arxiv_id (정규화된 제목으로)
    title_map = {}
    for p in papers:
        nt = norm_title(p["title"])
        if len(nt) >= _TITLE_MIN:
            title_map[nt] = p["arxiv_id"]

    debug = None
    if "--debug" in sys.argv:
        debug = sys.argv[sys.argv.index("--debug") + 1]

    graph = defaultdict(set)          # 인용하는 쪽 → 인용된 쪽
    stats = []

    for p in papers:
        aid = p["arxiv_id"]
        path = os.path.join(SRC_DIR, f"{aid}.tar.gz")
        files = read_all_text(path)
        blob = "\n".join(files.values())
        ents = entries_of(blob)

        by_id, by_title = set(), set()
        for key, body in ents:
            for m in _ARXIV_ID.findall(body):
                if m in corpus_ids and m != aid:
                    by_id.add(m)
            nb = norm_title(body)
            for nt, tid in title_map.items():
                if tid != aid and nt in nb:
                    by_title.add(tid)

        cited = by_id | by_title
        graph[aid] = cited
        stats.append((aid, len(files), len(ents), len(by_id), len(by_title), len(cited)))

        if debug and aid.startswith(debug):
            print(f"\n=== {aid} 진단 ===")
            print(f"파일 {len(files)}개: {list(files)[:8]}")
            print(f"bib 항목 {len(ents)}개")
            for k, b in ents[:3]:
                print(f"  [{k}] {' '.join(b.split())[:110]}")
            print(f"ID 매칭 {sorted(by_id)}")
            print(f"제목 매칭 {sorted(by_title)}")
            return

    # ── 출력 ────────────────────────────────
    print(f"{'arxiv_id':13}{'파일':>5}{'bib':>6}{'ID':>5}{'제목':>5}{'인용':>6}  제목")
    tmap = {p["arxiv_id"]: p["title"] for p in papers}
    for aid, nf, ne, ni, nt, nc in stats:
        mark = "⚠️" if ne == 0 else "  "
        print(f"{mark}{aid:11}{nf:5}{ne:6}{ni:5}{nt:5}{nc:6}  {tmap[aid][:40]}")

    edges = sum(len(v) for v in graph.values())
    cited_by = defaultdict(int)
    for src, dsts in graph.items():
        for d in dsts:
            cited_by[d] += 1

    print("\n" + "=" * 74)
    print(f"★ 코퍼스 내부 인용 {edges}건 (논문당 평균 {edges/len(papers):.1f})")
    print(f"  bib 항목 0개인 논문: {sum(1 for s in stats if s[2]==0)}편")

    print("\n★ 많이 인용된 논문 = bridge 질문의 '답' 후보")
    for aid, n in sorted(cited_by.items(), key=lambda x: -x[1])[:10]:
        print(f"  {n:2}회  {aid:12} {tmap[aid][:50]}")

    orphan = [p["arxiv_id"] for p in papers
              if not graph[p["arxiv_id"]] and cited_by[p["arxiv_id"]] == 0]
    if orphan:
        print(f"\n⚠️ 고립 {len(orphan)}편 — 인용도 피인용도 없다. bridge 재료가 안 된다")
        for a in orphan:
            print(f"     {a:12} {tmap[a][:50]}")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({k: sorted(v) for k, v in graph.items()}, f,
                  ensure_ascii=False, indent=2)
    print(f"\n→ {OUT}")

    print("\n※ 판단 기준")
    print("  50건 이상  → 클러스터 성립. Step 4 진행")
    print("  10~50건    → 빈약. 피인용 많은 논문 위주로 교체 검토")
    print("  10건 미만  → ⚠️ 선별을 다시 한다")


if __name__ == "__main__":
    main()
