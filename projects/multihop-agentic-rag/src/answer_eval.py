"""
answer_eval.py — 정답률 vs recall 분리 측정 (Phase A, W4)
경로: projects/multihop-agentic-rag/src/answer_eval.py

────────────────────────────────────────────────────────────
[왜 분리하나]
recall 은 "gold 문서를 잡았나", 정답률은 "답이 맞았나"를 잰다.
둘을 나란히 놓아야 검색의 실제 기여를 읽을 수 있다.

★ 2026-08-06 실측 결과 — 인과가 분해됐다 (n=32):
                P(gold 2/2)  P(정답|2/2)   EM
    pure           0.406        0.692     0.375
    rerank         0.656        0.571     0.406
    agentic        0.812        0.577     0.531

  조건부 정답률은 셋이 비슷하다. agentic 의 EM 우위는 전적으로
  **gold 2개 회수율(0.406 → 0.812)** 에서 온다.
  → "검색 recall 이 파이프라인 상한을 정한다"의 직접 증명.

  ⚠️ P(정답|2/2)에서 pure 가 1위인 것을 "pure 의 생성이 낫다"로
    읽으면 안 된다. 모집단이 다르다 — pure 가 gold 2개를 잡는
    케이스는 애초에 검색이 쉬운 질문이다(선택 편향).
────────────────────────────────────────────────────────────
"""

import re
import string
import unicodedata
from collections import Counter


# ─────────────────────────────────────────────
# [A] 정규화
# ─────────────────────────────────────────────
# ⚠️ LLM 답변에 특수 공백이 섞인다 (실측):
#     2026-08-04 U+00A0 (NBSP)      "Northern\u00a0Ireland"
#     2026-08-06 U+202F (NNBSP)     "Jang\u202fHyun-seung"
#   NFKC 가 U+00A0 는 처리하지만 U+202F 는 남긴다.
#   → 명시적으로 먼저 치환한다. 없으면 EM 이 조용히 0 이 된다.
_SPACE_LIKE = re.compile(r"[\u00a0\u2007\u2009\u200a\u200b\u202f\u2060]")


def normalize_answer(s):
    """소문자화 / 특수공백·구두점·관사 제거 / 공백 정규화."""
    if s is None:
        return ""
    s = _SPACE_LIKE.sub(" ", s)
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s


def exact_match(pred, gold):
    return float(normalize_answer(pred) == normalize_answer(gold))


def token_f1(pred, gold):
    """토큰 겹침 F1.

    ⚠️ gold 길이에 편향된다. gold 가 1토큰(yes/no/rock)인데
      예측이 15토큰이면 precision 이 1/15 로 폭락한다.
      comparison 유형에서 특히 가혹 — 형식 차이가 성능 차이로 보인다.
      (논문 Adaptive-RAG 도 F1 주지표를 쓰면서 이 편향을 언급 안 함)
    """
    p = normalize_answer(pred).split()
    g = normalize_answer(gold).split()
    if not p or not g:
        return float(p == g)

    common = Counter(p) & Counter(g)
    n_same = sum(common.values())
    if n_same == 0:
        return 0.0

    precision = n_same / len(p)
    recall = n_same / len(g)
    return 2 * precision * recall / (precision + recall)


def score_answer(pred, gold):
    return {"em": exact_match(pred, gold), "f1": token_f1(pred, gold)}


# ─────────────────────────────────────────────
# [B] 생성
# ─────────────────────────────────────────────
# ★★ 프롬프트는 agent.py 의 SYSTEM_PROMPT 와 **글자 단위로 동일**해야 한다.
#   2026-08-06 사건: pure/rerank 에만 "answer only" 지시가 있어
#   agentic 이 장문으로 답했고 EM 이 0.294 로 꼴찌였다.
#   통일 후 0.531 로 1위 — 성능 차이가 아니라 프롬프트 아티팩트였다.
#   ⚠️ 한쪽만 고치면 그 차이가 곧 결과 차이가 된다.
_FORMAT_RULE = (
    'Output ONLY the answer — a short phrase, name, date, number, or "yes"/"no".\n'
    "Do not write a sentence. Do not explain."
)

ANSWER_PROMPT = """Answer the question using ONLY the passages below.
If the passages do not contain the answer, say "unknown".

{format_rule}

Passages:
{context}

Question: {question}
Answer:"""


def generate_answer(question, pairs, provider=None):
    """검색 결과로 답을 생성한다. pairs: [(제목, 본문), ...]"""
    if provider is None:
        from src.llm import default_provider
        provider = default_provider()

    context = "\n\n".join(f"[{t}] {d}" for t, d in pairs)
    prompt = ANSWER_PROMPT.format(
        format_rule=_FORMAT_RULE, context=context, question=question
    )
    result = provider.chat([{"role": "user", "content": prompt}])
    return (result.text or "").strip()


# ─────────────────────────────────────────────
# [C] 분석 — recall 과 정답률의 어긋남
# ─────────────────────────────────────────────
def cross_table(records, mode, verbose=True):
    """gold 회수 정도 × 정답 여부 교차표.

    ⚠️ 2026-08-06 수정: 처음에는 recall > 0 을 '잡음'으로 뭉쳤다.
      HotpotQA 는 gold 가 항상 2개라 recall 0.5(한쪽만) 가 대부분인데
      그걸 '잡음'에 넣으니 표가 2행으로 붕괴했다.
      → 3분류(2/2, 1/2, 0/2)로 나눠야 의미가 보인다.

    ★ 실측(n=32): gold 2/2 면 정답률 57~69%, 1/2 면 9~33%.
      3~7배 차이 → "멀티홉은 문서 2개가 다 있어야 답이 나온다"의 증거.
      recall 0.5 는 절반 성공이 아니라 사실상 실패에 가깝다.
    """
    cells = Counter()
    for r in records:
        if r.get("error"):
            continue
        m = r[mode]
        rc = m["recall"]
        band = "full" if rc >= 1.0 else ("half" if rc > 0 else "none")
        res = "correct" if m.get("em", 0.0) > 0.5 else "wrong"
        cells[(band, res)] += 1

    if verbose:
        n = sum(cells.values())
        print(f"\n[{mode}] n={n}")
        for band, label in (("full", "gold 2/2"), ("half", "gold 1/2"), ("none", "gold 0/2")):
            c, w = cells[(band, "correct")], cells[(band, "wrong")]
            tot = c + w
            rate = f"{c/tot:.0%}" if tot else "—"
            print(f"  {label}: 정답 {c:2} / 오답 {w:2}  (정답률 {rate})")
    return cells


def decompose(records, mode):
    """EM 을 '검색 성공률 × 조건부 정답률' 로 분해한다.

    ★ 이 분해가 "agentic 우위는 생성이 아니라 검색에서 온다"를 보인다.
    """
    c = cross_table(records, mode, verbose=False)
    fc, fw = c[("full", "correct")], c[("full", "wrong")]
    hc, hw = c[("half", "correct")], c[("half", "wrong")]
    n = fc + fw + hc + hw
    if n == 0:
        return None
    return {
        "n": n,
        "p_full": (fc + fw) / n,
        "cond_full": fc / (fc + fw) if (fc + fw) else 0.0,
        "cond_half": hc / (hc + hw) if (hc + hw) else 0.0,
        "em": (fc + hc) / n,
    }


def print_decompose(records, modes=("pure", "rerank", "agentic")):
    print(f"\n{'':10}{'n':>4}{'P(gold2/2)':>12}{'P(정답|2/2)':>13}{'P(정답|1/2)':>13}{'EM':>8}")
    for m in modes:
        d = decompose(records, m)
        if d:
            print(f"{m:10}{d['n']:>4}{d['p_full']:>12.3f}{d['cond_full']:>13.3f}"
                  f"{d['cond_half']:>13.3f}{d['em']:>8.3f}")