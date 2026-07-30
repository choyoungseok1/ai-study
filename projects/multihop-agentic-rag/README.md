# 멀티홉 Agentic RAG

HotpotQA의 멀티홉 질문을 ReAct 루프로 분해해 검색하는 시스템. 단일 검색 RAG로는 도달할 수 없는 문서에 에이전트가 도달하는지를 recall로 정량 검증한다.

핵심 질문은 "에이전트가 더 잘하는가"가 아니라 **"더 잘하는 게 능력 때문인가 예산 때문인가"** 다. 에이전트는 검색을 여러 번 하므로 자연히 더 많은 문서를 본다. 그 차이를 통제한 비교가 이 프로젝트의 중심이다.

---

## 결과

bridge 질문 검색 recall@k (n=36). 단일 검색에 Agentic과 같은 문서 예산을 줬을 때:

| | recall@k |
|---|---|
| 단일 검색 (k=8.0) | 0.736 |
| Agentic 멀티홉 | 0.931 |

차이는 +0.195, 95% 신뢰구간 [0.029, 0.361]. 구간에 0이 없으므로 표본 우연으로 보기 어렵다.

### 왜 예산을 맞췄나

recall은 문서를 더 가져올수록 떨어지지 않는다. Agentic은 검색을 여러 번 하니 자연히 더 많이 본다. 이 상태로 비교하면 "많이 봐서 이긴 것"과 구분이 안 된다.

그래서 단일 검색에도 같은 예산을 줬다. 기준은 각 질문에서 **Agentic이 실제로 본 고유 문서 수**다. 전체 평균(8.7)을 일괄 적용하지 않고 질문별로 매칭했다. 홉이 3번 돌아도 재검색분이 겹치면 실제로 본 문서는 15개가 아니므로, 홉 수 × 5가 아니라 중복을 제거한 수를 썼다.

### 왜 recall인가

검색이 놓친 문서는 뒤에서 못 되살린다. 재정렬기는 후보 안에서 순서만 바꾸고, LLM은 컨텍스트에 없는 걸 근거로 쓸 수 없다. 검색 recall이 파이프라인의 상한이다.

실제로 이 코퍼스에서 상한@20은 0.869인데 재정렬 후 recall@5는 0.849였다. 1단계 검색이 못 가져온 0.131은 이후 어떤 단계로도 복구되지 않는다.

### 전체 결과

<details>
<summary>비교군 4종 × 질문 유형 (n=47)</summary>

| | pure (k=5) | rerank (k=5) | pure_budget | agentic |
|---|---|---|---|---|
| bridge (n=36, 평균 k=8.0) | 0.667 | 0.806 | 0.736 | 0.931 |
| comparison (n=11, 평균 k=11.0) | 0.864 | 0.909 | 0.909 | 1.000 |
| 전체 (n=47, 평균 k=8.7) | 0.713 | 0.830 | 0.777 | 0.947 |

- `pure` — bi-encoder top-5
- `rerank` — bi-encoder top-20 → cross-encoder로 5개로 압축
- `pure_budget` — bi-encoder top-k, k는 질문별 Agentic 고유 문서 수
- `agentic` — ReAct 멀티홉, 홉당 5개 검색

HotpotQA dev 서브셋 500개 중 앞 50문항. 3건은 tool call 스키마 오류로 제외(성공률 94%).

</details>

### 읽을 만한 지점 두 개

**재정렬이 예산 늘리기보다 낫다.** bridge에서 rerank는 0.806, pure_budget은 0.736이다. 재정렬은 문서 5개만 LLM에 주고 pure_budget은 평균 8개를 준다. 적게 주면서 더 잘한다. 후보를 넓히는 것보다 순위를 정확히 하는 쪽이 효율적이라는 뜻이다.

**bridge와 comparison이 다르게 움직인다.** comparison에서는 rerank와 pure_budget이 둘 다 0.909로 동률이고, Agentic의 우위도 +0.091로 작다. 두 엔티티가 질문에 모두 등장하므로 단일 검색으로도 도달할 수 있어서다. 이 비대칭이 질문 복잡도에 따라 검색 전략을 분기할 근거가 된다.

---

## 왜 Agentic인가

bridge 질문의 정답 문서 중 일부는 **원 질문으로 검색해서 나올 수 없다.** 질문에 그 문서를 가리킬 식별자가 없기 때문이다.

실제 사례 (idx=2):

> Q: "Dave Hemingway와 'A Little Time'을 듀엣한 가수는 어느 나라 출신인가?"
>
> gold: `A Little Time`, `Briana Corrigan`

원 질문으로 top-20을 뽑으면 `A Little Time`은 1위로 잡히지만 `Briana Corrigan`은 **20위 안에 없다.** 질문에 그 이름이 등장하지 않으므로 이 질의로는 도달할 수 없다. k를 100으로 키워도 마찬가지다. 순위 문제가 아니라 질의가 그 문서를 가리키지 못하는 문제다.

에이전트는 1홉에서 `A Little Time` 문서를 읽고 듀엣 상대가 누구인지 알아낸 뒤, 2홉에서 그 이름으로 검색해 도달한다. 에이전트의 가치는 같은 검색을 여러 번 하는 것이 아니라 **이전 관찰 결과로 새 검색어를 생성하는 것**이다.

### 주장의 범위

k를 늘리면 일부 케이스는 잡힌다. bridge에서 k를 5에서 8로 올렸을 때 recall이 0.667에서 0.736으로 올랐다. 그러나 Agentic의 0.931에는 미치지 못한다. 격차의 대부분은 순위 문제로 설명되지 않는다.

<details>
<summary>초기 n=10 실험에서 이 주장을 과대평가했던 기록</summary>

n=10에서는 k를 2배로 올려도 10문항 전부 recall 변화가 0이었고, 이를 "k를 늘려도 전혀 잡히지 않는다"는 증거로 삼았다. n=47로 확대하니 +0.069로 올랐다. 작은 표본에서 나온 "완벽한 0"은 신호가 아니라 표본 부족의 징후였다.

</details>

---

## 아키텍처

```
질문
 │
 ├─ 검색 (bi-encoder, all-MiniLM-L6-v2)          top-20
 │        │
 │        └─ 재정렬 (cross-encoder, bge-reranker-base)  top-5
 │
 ├─ 에이전트 (ReAct 루프, Groq function calling)
 │        관찰 → 새 검색어 생성 → 재검색 (최대 6홉)
 │
 ├─ 평가 (recall@k, context_precision)
 │
 └─ 서빙 (FastAPI)   ← 진행 중
```

### 설계 결정

**영어 전용 임베딩** — 코퍼스와 질문이 모두 영어인데 multilingual 모델은 384차원 공간을 50개 언어에 나눠 쓴다. 언어 간 정렬은 이 태스크에 필요 없는 능력이고, 그 대가로 영어 의미 구분에 쓸 표현 용량이 줄어든다. recall@5가 0.57에서 0.739로 올랐다. multilingual이 레이어 2배, 파라미터 5배인데도 더 나빴다.

**2단계 검색** — bi-encoder는 질문과 문서를 따로 인코딩해 빠르지만 둘의 관계를 보지 못해 순위가 거칠다. cross-encoder는 함께 읽어 정밀하지만 코퍼스 전체에 쓰면 질문당 4928회 forward가 필요하다. bi로 20개 추리고 cross로 재정렬해 절충했다 (0.739 → 0.849).

**open-domain 검색** — HotpotQA는 질문마다 후보 문단 10개를 제공하지만 전체 코퍼스 4928개를 인덱싱했다. 후보가 10개면 정답이 애초에 그 안에 있어서 "검색으로 도달 불가능한 문서"라는 개념이 사라지고, 이 프로젝트가 측정하려는 대상도 함께 사라진다. 대가로 recall 절대값이 낮다 (상한@20 = 0.869).

**LangChain 미사용** — ReAct 루프를 raw Groq SDK로 직접 구현했다. request → execute → respond 왕복을 손으로 짜면 tool calling의 전체 메커니즘이 드러나고, 추상화가 감추는 버그를 피할 수 있다.

---

## 평가 지표

recall@k와 context_precision을 **합치지 않고 병렬 보고**한다. 전자는 "놓친 정답이 있나", 후자는 "가져온 것 중 쓸모없는 게 많나"에 답한다. 가중합으로 뭉개면 두 지표가 서로 다른 방향을 가리킬 때의 정보가 사라진다.

<details>
<summary>context_precision을 LLM judge로 구현했고, 그 한계를 규명한 기록</summary>

RAGAS 대신 judge를 직접 호출했다. 0.4.x에서 API가 크게 바뀌어 안정화 시간이 불확실했고, judge 호출을 직접 통제해야 Groq의 `n=1` 제약과 rate limit을 회피할 수 있었다. 로직이 단순해 직접 구현하는 편이 "이 숫자가 어떻게 나왔는지"를 코드로 설명할 수 있다.

판정 결과를 육안 검수하다 문제를 발견했다. judge가 **gold 문서를 무관으로 판정**했다. 위 사례의 `A Little Time`이 그렇다. 듀엣 상대를 알려주는 bridge 문서인데, 프롬프트에 "intermediate step도 유용하면 yes"를 명시했음에도 judge가 질문을 표면적으로만 보고("국적 정보가 없으니 무관") 걸러냈다.

gold 문서를 자동 relevant로 고정하자 이번에는 지표가 recall의 변형으로 붕괴했다. bridge 세 비교군이 0.33 부근으로 수렴했다. 사실상 `gold 잡은 수 / 검색한 수`가 되어 judge 고유의 신호가 사라진 것이다.

RAGAS 원 논문에서도 context relevance는 세 지표 중 인간 일치도가 가장 낮았고(0.70), 저자들도 긴 컨텍스트에서 핵심 문장 선별에 실패한다고 보고했다. 그리고 RAGAS는 reference-free를 전제로 설계됐다. gold 라벨이 있는 이 태스크는 논문이 상정한 조건이 아니다.

결론: **집계 절대값은 신뢰하지 않고 bridge/comparison 비대칭의 방향성만 근거로 사용한다.** comparison에서 agentic이 정밀도 손해를 본다는 결과는 두 judge 방식에서 모두 일관되게 나타났다.

</details>

### 알려진 한계

**recall ≠ 정답률.** gold 문서를 놓쳤는데도 LLM의 파라메트릭 지식으로 정답이 나오는 경우가 있다. 검색 성능과 답변 성능은 분리해서 측정해야 한다.

**tool calling 성공률 94%.** `gpt-oss-120b`가 스키마에 없는 인자를 생성하거나 등록되지 않은 툴을 호출하는 경우가 50문항 중 3건 있었다. 실패를 `error` 필드로 격리해 평균이 오염되지 않게 했다.

**comparison에서 분해가 손해다.** 두 엔티티가 질문에 모두 있는데 불필요하게 쿼리를 분해하면, 원 질문이 잡던 문서를 놓칠 수 있다. 한 케이스에서 Agentic은 단일 검색보다 문서를 더 많이 보고도 recall이 낮았다.

---

## 구조

```
projects/multihop-agentic-rag/
├── src/
│   ├── retrieve.py            검색 + 재정렬 (Chroma 영속)
│   ├── agent.py               ReAct 루프, 비교군 4종 평가, JSONL 저장
│   └── context_precision.py   LLM judge 기반 정밀도 지표
├── notebooks/                 실험
└── data/                      코퍼스·인덱스·평가 결과 (gitignore)
```

실험은 노트북에서, 굳은 것은 `src`로 옮긴다. 평가 로그는 JSONL로 append하며 원본만 저장한다. 홉 수나 고유 문서 수 같은 파생값은 분석 시점에 계산한다. 집계값을 저장하면 정의가 바뀔 때 전체를 재실행해야 한다.

---

## 실행

```bash
pip install -r requirements.txt

# .env 설정
GROQ_API_KEY=...
CHROMA_DIR=C:\path\to\chroma    # ASCII 경로여야 함 (아래 참고)

python -m src.retrieve    # 코퍼스 인덱싱 (CPU, 약 2분)
python -m src.agent       # 비교군 평가
```

`python 경로/파일.py`가 아니라 `python -m src.모듈`로 실행해야 한다. 전자는 `sys.path[0]`이 파일이 있는 폴더가 되어 `from src.X import Y`가 실패한다.

`CHROMA_DIR`은 ASCII 경로로 지정한다. 비ASCII 경로에서는 chroma-hnswlib(C++ 확장)이 인덱스를 로드하지 못한다. sqlite를 읽는 `count()`는 통과하는데 hnsw를 읽는 `query()`만 실패하는 비대칭이 단서였다.

---

## 스택

| | |
|---|---|
| 임베딩 | sentence-transformers `all-MiniLM-L6-v2` (로컬 CPU) |
| 재정렬 | `BAAI/bge-reranker-base` |
| 벡터 DB | Chroma 0.6.3 |
| LLM | Groq `openai/gpt-oss-120b` |
| 데이터셋 | HotpotQA (dev, hard, distractor 설정에서 코퍼스 재구성) |

로컬 GPU가 2GB라 LLM 추론은 무료 호스팅 API를 쓴다. 임베딩과 벡터 검색은 CPU에서 돌린다.

---

## 진행 상황

- [x] 검색 + 재정렬 파이프라인
- [x] ReAct 멀티홉 루프
- [x] 비교군 4종 평가 + 예산 통제 실험 (n=47)
- [ ] FastAPI 서빙
- [ ] 정체 감지 (홉 간 새 문서가 0개면 조기 종료)
- [ ] arXiv 도메인 확장
