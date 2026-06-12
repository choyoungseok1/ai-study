# Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

- **arxiv**: https://arxiv.org/abs/2310.11511
- **학회**: ICLR 2024 (Oral)
- **리뷰 날짜**: 2026-06-11

---

## 한 줄 요약

기본 RAG는 *무조건* 고정 개수의 문서를 검색해 붙이지만, **Self-RAG는 단일 LM이 reflection token으로 (1) 검색이 필요한지 스스로 판단하고 (2) 자기 생성물을 스스로 비평**(관련성·근거지지·유용성)하도록 학습시켜 — **필요할 때만 검색하고 근거에 충실한 답**을 만든다.

---

## 섹션별 정리

### Introduction
- 기존 RAG의 문제 **두 가지**:
  1. **무차별·고정 검색** — 필요 여부·관련성과 무관하게 정해진 개수를 붙임 → 무관하거나 불필요한 passage로 답이 *오히려 나빠질 수 있음*
  2. **faithfulness 미보장** — 생성물이 검색된 근거로 뒷받침되는지 보장 안 됨 (모델이 근거를 따르도록 학습된 게 아님)
- 해결: **reflection token (Retrieval + Critique)**을 단일 LM이 본문과 함께 생성 → 적응적 검색 + 자기비평. 추론 시 토큰 가중치로 **행동 조절(controllable)** 가능.
- 결과: Self-RAG(7B/13B)가 표준 RAG는 물론 ChatGPT까지 능가.

### Related Work (차별점 중심)
- **RAG / 적응형 RAG**: "언제 검색할지"는 정하지만, 검색 결과의 관련성/자기 답의 근거지지는 *비평하지 않음* → Self-RAG는 그 자기비평을 추가
- **Concurrent (문서 필터링)**: 검색 결과를 *별도 모듈*로 필터/재순위 → Self-RAG는 *단일 LM 안*에서 통합
- **Critics 활용**: RLHF식 강화학습 또는 추론 시 별도 critic으로 재순위 → 추론 비용↑ → Self-RAG는 critique를 *지도학습으로 모델에 내재화*, 추론 시 별도 critic 불필요
- **관통**: 적응검색 + 자기비평을 *하나의 LM*에, *지도학습*으로, *추론 효율 유지*하며 통합

### Method (3장) — 가장 중요
- **Segment 단위 생성**: 답을 한 번에 안 뽑고 **문장(segment) 단위**로 끊어, 문장마다 `[검색? → 생성 → 비평]`을 반복 (답 y = [문장1, 문장2, …])
- **Reflection token 4종**:
  | 토큰 | 의미 |
  |---|---|
  | **Retrieve** | 지금 외부 지식(검색)이 필요한가 |
  | **ISREL** | 검색된 문서가 *질문과* 관련 있는가 (문서 ↔ 질문) |
  | **ISSUP** | 생성한 문장이 *그 문서로* 뒷받침되는가 = faithfulness (생성문장 ↔ 문서) |
  | **ISUSE** | 답이 유용한가 (1~5) |
- **학습**:
  - **Critic C**: reflection token 예측 학습. *학습 데이터는 GPT-4로 라벨을 distill*해 만들고, 그걸로 Llama 기반 C를 학습
  - **Generator M**: C + 검색기로 코퍼스에 *외부문서 + reflection token을 미리 삽입(증강)* → 그 데이터로 **다음 토큰 예측(지도학습)**으로 M 학습
  - ※ M은 **Llama2(7B/13B)** 기반. GPT-4는 *critic 라벨 만드는 선생님*일 뿐, 최종 모델엔 GPT 없음. **RL 안 씀 (순수 지도학습)**
- **추론 + 통제**: ① 적응형 검색(Retrieve) ② 검색 시 passage별 후보를 *병렬* 생성 + 비평 ③ 비평 점수로 **best segment 선택** ④ 추론 시 비평 토큰 *가중치 조절*로 맞춤 제어(재학습 없이 faithfulness 강조 등)

### Figure 1 (추론 과정 한 장 요약)
- **위** "How did US states get their names?" (사실 질문): `[Retrieve]` → passage 3개 병렬로 후보 문장 + 비평(Relevant/Supported 등) → 비평으로 best 선택 (① > ③ > ②)
- **아래** "Write an essay…" (창작): `[No Retrieval]` → 검색 없이 바로 생성 ← *적응형 검색*의 핵심 (기본 RAG는 이것도 검색함)

### Experiments (4장)
- **태스크**: 폐쇄형(PubHealth 사실검증, ARC 과학객관식), 단답 QA(PopQA, TriviaQA), 장문(ALCE-ASQA 인용포함, 전기생성 FactScore)
- **베이스라인**: 검색 없는 LLM(Llama2, ChatGPT 등) + 표준 RAG(검색 변형들)
- **Self-RAG**: Llama2 7B/13B, reflection token 증강 데이터(~15만)로 학습, 기성 검색기(Contriever/위키)
- **지표**: 정확도, FactScore, 인용 precision/recall, MAUVE

### Results (5장)
- **Self-RAG(7B/13B)가 검색 없는 LLM·표준 RAG·ChatGPT까지 대부분 태스크에서 능가** (13B > 7B)
- 특히 **사실성·인용 정확도**에서 큰 향상 (ISSUP 자기검증 효과)
- **Ablation**: 검색·비평·선택을 빼면 성능↓ → 각 컴포넌트가 기여함을 확인
- **Controllability 실증**: 추론 시 ISSUP 가중치↑ → 인용 정확도↑ (재학습 없이)
- **효율**: 적응형 검색이라 항상 검색하는 RAG보다 효율적이면서 더 정확

---

## 새로 알게 된 것
- reflection token으로 **검색 여부 결정 + 자기비평을 모델에 내재화** → **agentic RAG**의 대표 사례 (ReAct와 같은 결)
- 답을 **segment(문장) 단위**로 생성하며 문장마다 검색·비평·선택
- critique를 **RL 없이 지도학습**으로 심는 법: critic 라벨(GPT-4 distill) → 코퍼스 증강 → generator 지도학습
- **추론 시 비평 가중치 조절**로 재학습 없이 행동(faithfulness 등) 통제 가능
- 자기비평 덕에 **더 작은 모델이 큰 모델/표준 RAG보다 사실성·인용에서 우수**

## 이해 안 된 것 (처음 헷갈렸다가 해결한 것 포함)
- **Segment가 뭔지** 모호했음 → 생성의 한 단위(보통 한 문장)이고, 문장 단위로 검색·비평·선택을 반복하는 것
- **ISREL vs ISSUP 혼동** → ISREL = 문서↔질문 *관련성*, ISSUP = 생성문장↔문서 *지지(faithfulness)*. 둘은 다름
- **Generator가 GPT인 줄 오해** → 아니고 **Llama2**. GPT-4는 critic의 *학습 라벨* 만드는 데만 쓰임
- **Figure 1 동작 흐름** → 적응검색 → passage 병렬 후보+비평 → best 선택. 위(검색)/아래(No Retrieval) 대비로 이해

---

## 비고
- Appendix(구현 디테일·추가 실험)는 스킵. 직접 구현(agentic RAG 프로젝트) 들어갈 때 다시 펴면 됨 — 특히 *reflection token 판정 기준* + *GPT-4 라벨링 프롬프트*
- 연결: **Week 9의 "Agentic RAG / ReAct" · "RAG 평가"** 와 직결 (이 논문이 그 방향의 대표 사례)
