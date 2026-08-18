"""
Phase B Step 2 — LaTeX source 수집 + 섹션 분할
2026-08-18 (Week 18)

왜 LaTeX 인가
  gold 를 **(arxiv_id, section)** 으로 정의했으므로 섹션 경계가 정확해야 한다.
  - PDF 파싱: 2단 조판에서 섹션이 뭉개진다 → 판정 불가
  - arXiv HTML: 깔끔하지만 **2023-12 이후 제출분만** 있다.
    우리 코퍼스의 2022~2023 논문 7편(Self-RAG, ReAct, RAGAS, ARES 등)이
    거기 걸리는데, 하필 **bridge 질문의 '답이 되는' 허브 논문들**이라 뺄 수 없다
  - LaTeX source: `\\section{}` 이 그대로 있고 커버리지가 가장 넓다

⚠️ HTML 과 LaTeX 를 섞으면 안 된다. 섹션 제목을 미묘하게 다르게 뽑으면
   gold 판정이 논문마다 달라진다. **한 방식으로 통일한다.**

★ 덤 — 인용 그래프가 공짜로 나온다
  arXiv API 는 참고문헌을 주지 않아 8/17에 막혔던 부분인데,
  LaTeX 의 `\\cite{}` 와 `\\bibitem{}` 에 다 들어 있다.
  섹션별 인용 키를 기록해두면 **어느 논문 쌍이 bridge 재료인지** 자동으로 나온다.
  → Step 4(QA쌍 수작업) 병목이 줄어든다

⚠️ 저작권 — 본문은 재배포 불가. data/ 는 gitignore 안이다.
   README 에는 재구성 절차만 적는다 (Phase A 의 HotpotQA 와 동일 처리).

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.fetch_sources          # 받기만
      python -m scripts.fetch_sources --parse  # 받고 파싱까지
"""
import os
import re
import io
import sys
import json
import time
import gzip
import tarfile
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
ARXIV_DIR = os.path.join(_DATA, "arxiv")
SRC_DIR = os.path.join(ARXIV_DIR, "src")
SELECTED = os.path.join(ARXIV_DIR, "selected.json")
OUT = os.path.join(ARXIV_DIR, "sections.json")

SLEEP_SEC = 3.0     # ⚠️ arXiv e-print 는 API 보다 제한이 엄격하다
UA = {"User-Agent": "phaseB-corpus-builder (academic use)"}


# ═════════════════════════════════════════════
# [A] 내려받기
# ═════════════════════════════════════════════
def base_id(arxiv_id):
    """버전 접미사 제거. '2210.03629v3' → '2210.03629'

    ⚠️ 버전을 붙이면 그 버전이 고정된다. 최신판을 쓰려면 빼는 게 맞고,
      대신 나중에 재현할 때 판본이 달라질 수 있다는 걸 기록해둔다.
    """
    return re.sub(r"v\d+$", "", arxiv_id)


def download(arxiv_id, force=False):
    aid = base_id(arxiv_id)
    dst = os.path.join(SRC_DIR, f"{aid}.tar.gz")
    if os.path.exists(dst) and not force:
        return dst, "캐시"
    os.makedirs(SRC_DIR, exist_ok=True)
    url = f"https://arxiv.org/e-print/{aid}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    with open(dst, "wb") as f:
        f.write(data)
    return dst, f"{len(data)/1024:.0f}KB"


def read_tex_files(path):
    """압축 해제해 .tex 내용을 {파일명: 텍스트} 로.

    ⚠️ e-print 는 세 형태로 온다:
      1. tar.gz (여러 파일)  2. gz 로 압축된 단일 .tex  3. 드물게 PDF only
    """
    out = {}
    try:
        with tarfile.open(path) as tf:
            for m in tf.getmembers():
                if m.isfile() and m.name.endswith(".tex"):
                    raw = tf.extractfile(m).read()
                    out[m.name] = raw.decode("utf-8", errors="replace")
        return out, "tar"
    except tarfile.ReadError:
        pass
    try:
        with gzip.open(path, "rb") as f:
            raw = f.read()
        if raw[:4] == b"%PDF":
            return {}, "PDF-only"
        return {"main.tex": raw.decode("utf-8", errors="replace")}, "단일"
    except Exception as e:
        return {}, f"실패({type(e).__name__})"


# ═════════════════════════════════════════════
# [B] LaTeX → 섹션
# ═════════════════════════════════════════════
_COMMENT = re.compile(r"(?<!\\)%.*")
_ENV_DROP = re.compile(
    r"\\begin\{(figure\*?|table\*?|equation\*?|align\*?|tabular|algorithm.*?)\}"
    r".*?\\end\{\1\}", re.S)
_CITE = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}")
_SIMPLE_CMD = re.compile(r"\\(?:textbf|textit|emph|texttt|text|mbox|underline)\{([^{}]*)\}")
_LEFTOVER_CMD = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])*(?:\{[^{}]*\})?")
_SECTION = re.compile(r"\\(section|subsection)\*?\{((?:[^{}]|\{[^{}]*\})*)\}")
_BIBITEM = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})", re.S)
_ARXIV_IN_BIB = re.compile(r"(?:arXiv[:\s]*|abs/)(\d{4}\.\d{4,5})", re.I)


def find_main(tex_files):
    """\\documentclass 가 있는 파일이 본체."""
    cands = [n for n, t in tex_files.items() if "\\documentclass" in t]
    if not cands:
        return max(tex_files, key=lambda n: len(tex_files[n])) if tex_files else None
    return min(cands, key=len)      # 경로가 짧은 쪽이 보통 루트


def expand_inputs(tex_files, main, depth=0):
    """\\input{} / \\include{} 를 펼친다.

    ⚠️ 이걸 안 하면 섹션이 별도 파일에 있는 논문에서 본문이 통째로 빈다.
    """
    if depth > 5 or main not in tex_files:
        return tex_files.get(main, "")
    text = tex_files[main]

    def sub(m):
        name = m.group(1).strip()
        for cand in (name, name + ".tex", "./" + name + ".tex"):
            for key in tex_files:
                if key == cand or key.endswith("/" + cand):
                    return expand_inputs(tex_files, key, depth + 1)
        return ""

    return re.sub(r"\\(?:input|include)\{([^}]*)\}", sub, text)


def to_plain(s):
    """LaTeX → 평문. 인용 키는 따로 뽑고 본문에서는 제거한다."""
    s = _COMMENT.sub("", s)
    s = _ENV_DROP.sub(" ", s)
    s = _CITE.sub(" ", s)
    s = re.sub(r"\$[^$]*\$", " ", s)          # 인라인 수식
    for _ in range(3):                        # 중첩 명령 몇 겹
        s = _SIMPLE_CMD.sub(r"\1", s)
    s = _LEFTOVER_CMD.sub(" ", s)
    s = s.replace("{", " ").replace("}", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def split_sections(body):
    """(섹션 제목, 본문, 인용키 목록) 리스트.

    ★ gold 정의가 (arxiv_id, section) 이므로 **제목 표기가 일관되어야** 한다.
      to_plain 을 제목에도 적용해 같은 규칙으로 정규화한다.
    """
    marks = [(m.start(), m.group(1), to_plain(m.group(2))) for m in _SECTION.finditer(body)]
    if not marks:
        return []
    out = []
    for i, (pos, kind, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        raw = body[pos:end]
        cites = sorted({k.strip() for m in _CITE.finditer(raw)
                        for k in m.group(1).split(",") if k.strip()})
        text = to_plain(raw)
        # 제목 줄 자체를 본문에서 뺀다
        text = text[len(title):].strip() if text.startswith(title) else text
        if len(text) < 100:                   # 표지·감사말 등
            continue
        out.append({"kind": kind, "title": title, "text": text, "cites": cites})
    return out


def parse_bibliography(body):
    """bib 키 → 참조된 arXiv ID. 인용 그래프 재료."""
    out = {}
    for m in _BIBITEM.finditer(body):
        key, entry = m.group(1).strip(), m.group(2)
        ids = _ARXIV_IN_BIB.findall(entry)
        if ids:
            out[key] = ids[0]
    return out


# ═════════════════════════════════════════════
def main():
    do_parse = "--parse" in sys.argv
    sel = json.load(open(SELECTED, encoding="utf-8"))
    print(f"대상 {len(sel)}편\n")

    fetched = []
    for i, rec in enumerate(sel, 1):
        aid = base_id(rec["arxiv_id"])
        try:
            path, how = download(aid)
            print(f"[{i:2}/{len(sel)}] {aid:12} {how:8} {rec['title'][:44]}")
            fetched.append((aid, path, rec))
        except Exception as e:
            print(f"[{i:2}/{len(sel)}] {aid:12} FAIL  {type(e).__name__}: {str(e)[:40]}")
            continue
        if how != "캐시":
            time.sleep(SLEEP_SEC)

    if not do_parse:
        print("\n파싱하려면 --parse 를 붙여 다시 실행")
        return

    # ── 파싱 ────────────────────────────────
    print("\n" + "=" * 70)
    papers, problems = [], []
    for aid, path, rec in fetched:
        tex, kind = read_tex_files(path)
        if not tex:
            problems.append((aid, kind))
            print(f"  ⚠️ {aid:12} {kind}")
            continue
        main_f = find_main(tex)
        body = expand_inputs(tex, main_f)
        secs = split_sections(body)
        bib = parse_bibliography(body)
        if not secs:
            problems.append((aid, "섹션 0개"))
            print(f"  ⚠️ {aid:12} 섹션 0개 (main={main_f})")
            continue
        papers.append({
            "arxiv_id": aid,
            "title": rec["title"],
            "group": rec.get("group"),
            "sections": secs,
            "bib_arxiv": bib,        # bib 키 → arXiv ID
        })
        words = sum(len(s["text"].split()) for s in secs)
        print(f"  {aid:12} 섹션 {len(secs):2}개  {words:6,}단어  "
              f"bib에서 arXiv ID {len(bib):3}개")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    # ── 요약 ────────────────────────────────
    print("\n" + "=" * 70)
    print(f"파싱 성공 {len(papers)}편 / 문제 {len(problems)}편  →  {OUT}")
    for aid, why in problems:
        print(f"  ❌ {aid}: {why}")

    tot_sec = sum(len(p["sections"]) for p in papers)
    tot_word = sum(len(s["text"].split()) for p in papers for s in p["sections"])
    print(f"\n섹션 {tot_sec}개 / 약 {tot_word:,}단어 ≈ {tot_word*1.3:,.0f}토큰")
    for c in (200, 400, 800):
        print(f"  청크 {c:3}토큰 → 문서 약 {tot_word*1.3/c:,.0f}개")

    # ★ 인용 그래프 — 코퍼스 내부 인용만
    ids = {p["arxiv_id"] for p in papers}
    edges = 0
    for p in papers:
        inner = {v for v in p["bib_arxiv"].values() if v in ids}
        edges += len(inner)
    print(f"\n★ 코퍼스 내부 인용 {edges}건 — bridge 질문 재료")
    print("  ⚠️ 0에 가까우면 코퍼스가 클러스터를 이루지 못한 것이다.")
    print("     그 경우 bridge 질문을 만들 수 없으므로 논문 선별을 다시 해야 한다.")


if __name__ == "__main__":
    main()
