# 이번 주 논문 추천 (2026-07-20 ~ 07-23)

## 현재 학습 컨텍스트 (Notion 학습용 캘린더 기준)

**Week 14 · 프로젝트 "멀티홉 Agentic RAG 시스템" (Phase A, 목표 8/15)**

| 날짜 | 할일 |
|---|---|
| 07-20 (오늘) | 논문 1편: ReAct (2210.03629) 리뷰 + Lv2 1문제 |
| 07-21 | [W2-4] 비교군 3종 확정 (순수 RAG / 재정렬 RAG / Agentic 베이스라인) |
| 07-22 | 버퍼 + 주간 회고 + 모의면접 (임베딩/평가지표/왜 Agentic 방어 카드) |
| 07-23 | 예비/이월 또는 W3 선행 |

→ **키워드: 멀티홉 검색, 에이전트 제어 흐름, cross-encoder 재정렬, RAGAS 정량 평가, 비교군 설계.**
아래 추천은 전부 이 4개 축에 붙였습니다. 특히 07-21 "비교군 3종 확정"과 다음 주 W3 정량 평가에 바로 쓸 수 있는 것 위주.

---

## 1. A-RAG: Scaling Agentic Retrieval-Augmented Generation via Hierarchical Retrieval Interfaces

- **arXiv**: https://arxiv.org/abs/2602.03442 (2026-02)
- **코드**: https://github.com/Ayanami0730/arag ✅ (코드 + 평가 스위트 공개)
- **분량**: 본문 기준 15p 내외 (부록 별도)

**초록 요약**
기존 RAG는 (1) 한 번에 passage를 검색해 입력에 이어붙이거나, (2) 워크플로를 미리 정의하고 모델이 단계별로 실행하게 하는 두 패러다임에 머물러 있어, 모델이 검색 의사결정에 직접 참여하지 못한다. A-RAG는 계층적 검색 인터페이스를 모델에 그대로 노출하는 Agentic RAG 프레임워크로, `keyword_search` · `semantic_search` · `chunk_read` 세 가지 도구를 제공해 에이전트가 여러 granularity를 넘나들며 적응적으로 검색하게 한다. 여러 open-domain QA 벤치마크에서 동등하거나 더 적은 검색 토큰으로 기존 방식을 일관되게 상회했으며, 모델 크기·test-time compute에 따른 스케일링도 체계적으로 분석했다.

**추천 이유 3줄**
1. 지금 하고 있는 "run_agent의 search 도구로 `retrieve_and_rerank` 등록"과 정확히 같은 설계 문제를 다룹니다 — 도구를 하나로 줄 것이냐, keyword/semantic/chunk_read로 쪼갤 것이냐.
2. 07-21 비교군 3종 확정에 직접 인용 가능: "워크플로 사전정의(=재정렬 RAG) vs 모델이 검색 결정(=Agentic)" 구분이 이 논문의 핵심 프레이밍이라 베이스라인 정의 근거가 됩니다.
3. 검색 토큰 대비 성능을 같이 보고해서, "왜 Agentic인가" 면접 방어 카드에 비용-성능 축을 추가할 수 있습니다 (성능만 말하면 반박당하는 지점).

**한글 참고**: [Agentic RAG for Dummies (LangGraph 기반 오픈소스) — PyTorchKR](https://discuss.pytorch.kr/t/agentic-rag-for-dummies-agentic-rag-feat-langgraph/8783) / [Google Research의 Agentic RAG: 멀티 에이전트 검색 — PyTorchKR](https://discuss.pytorch.kr/t/google-research-agentic-rag/10599)

---

## 2. AgenticRAGTracer: A Hop-Aware Benchmark for Diagnosing Multi-Step Retrieval Reasoning in Agentic RAG

- **arXiv**: https://arxiv.org/abs/2602.19127 (2026-02-22)
- **코드/데이터**: https://github.com/YqjMartin/AgenticRAGTracer ✅
- **분량**: 벤치마크 논문, 본문 10p대

**초록 요약**
멀티홉 추론은 Agentic RAG 능력 평가의 핵심 테스트베드지만, 기존 벤치마크는 최종 질문과 정답만 제공하고 atomic question들을 최종 멀티홉 질의로 이어주는 **중간 hop 단위 질문이 없다**. 그래서 에이전트가 몇 번째 스텝에서 실패했는지 분석할 수 없다. AgenticRAGTracer는 LLM으로 대부분 자동 구축된 최초의 step-by-step 검증 가능한 Agentic RAG 벤치마크로, 다중 도메인 1,305개 데이터포인트를 담고 기존 주요 벤치마크와 겹치지 않는다. GPT-5조차 가장 어려운 구간에서 EM 22.6%에 그쳤고, hop 단위 진단 결과 실패의 주원인은 추론 사슬의 왜곡 — 너무 일찍 붕괴하거나 과도하게 늘어지는 것 — 즉 과제의 논리 구조에 맞게 스텝을 배분하지 못하는 문제였다.

**추천 이유 3줄**
1. 07-18 태스크였던 "멀티홉 트레이스 분석(A→B 다단계 검색이 실제로 도는지)"을 **정량 지표로 바꾸는 방법**이 이 논문에 있습니다 — 트레이스를 눈으로 보는 단계에서 hop-level 채점으로 넘어갈 수 있습니다.
2. HotpotQA는 supporting facts는 주지만 hop 단위 중간 질문은 없어서, 이 논문의 hop-aware 진단 프레임을 빌려오면 "재정렬이 몇 번째 hop에서 효과를 내는가"를 보일 수 있습니다 — 포트폴리오 차별점.
3. "조기 붕괴 vs 과도 확장" 실패 유형 분류는 07-19 프롬프트 튜닝(질문 분해 유도)의 결과를 설명하는 언어로 그대로 쓸 수 있습니다.

**한글 참고**: [RAG기반 Multi-Agent 구현 (ReAct 에이전트 구성) — SK DevOcean](https://devocean.sk.com/blog/techBoardDetail.do?ID=168018&boardType=techBlog)

---

## 3. Transforming LLMs into Efficient Cross-Encoders via Knowledge Distillation for RAG Reranking

- **arXiv**: https://arxiv.org/abs/2607.11933 (2026-07-11, **가장 최신**)
- **분량**: **6페이지, figure 4개** ✅ (오늘 ReAct 리뷰와 병행해도 부담 없음)
- **코드**: 저장소 명시 없음 ⚠️ — 다만 Unsloth + LoRA + 4bit 양자화라 재현 스택 자체는 전부 오픈

**초록 요약**
Cross-encoder는 RAG 파이프라인에서 높은 재정렬 정확도를 내지만 quadratic 추론 비용 탓에 실시간 서빙이 어렵다. 저자들은 LLaMA 3 (8B)를 drop-in 리랭커로 파인튜닝하는 2단계 파이프라인을 제안한다: Unsloth 프레임워크 + LoRA 어댑터로 커스텀 query-document 관련성 데이터셋에 SFT → 4-bit 양자화로 효율적 추론. 이 모델이 BM25 + dense vector search 이중 검색 RAG 파이프라인의 cross-encoder를 대체한다. 도메인 특화 QA 벤치마크에서 **RAGAS로 평가**한 결과 cross-encoder 베이스라인 대비 answer relevancy +14%, **context precision +16%**, answer similarity +19%, answer correctness +21%를 달성했다.

**추천 이유 3줄**
1. 지금 쓰는 스택(**BM25+dense 이중 검색 → cross-encoder 재정렬 → RAGAS 평가**)과 거의 1:1로 겹칩니다. 남의 프로젝트 구성이 내 것과 같을 때가 벤치마크 수치를 비교하기 가장 좋습니다.
2. **context precision +16%**는 07-15 W1 완료 기준("supporting facts가 상위에 잡히는지")의 정량 대응물 — 내 재정렬 효과가 어느 정도면 정상 범위인지 감을 잡는 기준선이 됩니다.
3. 6페이지짜리 워크숍성 논문이라 부담이 없고, 07-22 모의면접 "임베딩 선택 / 왜 재정렬인가" 방어 카드에 최신 근거 한 줄을 얹을 수 있습니다.
   ⚠️ 단, comments에 "This work was completed in 2024"라 적혀 있고 코드 공개가 없습니다. 수치는 참고용으로만 쓰고 인용 시 이 점 명시 권장.

**한글 참고**: [한국어 Reranker를 활용한 RAG 성능 올리기 — AWS 기술 블로그](https://aws.amazon.com/ko/blogs/tech/korean-reranker-rag/) / [Cross Encoder Reranker — 랭체인 한국어 노트](https://wikidocs.net/253836) / [RAGAS metrics 정리 — velog](https://velog.io/@yoonene/RAGAS-metrics-%EC%A0%95%EB%A6%AC)

---

## 읽는 순서 제안

1. **오늘(07-20)**: 예정대로 ReAct(2210.03629) 리뷰가 메인. 여유가 있으면 **3번(6p)**만 곁들이기 — 재정렬 수치 감각용.
2. **07-21 (비교군 3종 확정일)**: **1번 A-RAG**를 먼저. 베이스라인 3종의 경계를 어떻게 그을지에 대한 논거가 여기 있습니다.
3. **07-22~23 (버퍼/예비)**: **2번 AgenticRAGTracer**. 다음 주 W3 정량 평가 설계 직전에 읽는 게 효과가 가장 큽니다.

**우선순위 하나만 고른다면 → 1번 A-RAG.** 코드+평가 스위트가 공개돼 있고, 이번 주 태스크(도구 인터페이스 설계 + 비교군 정의) 양쪽에 다 걸칩니다.

---

## 이번 실행에서의 판단 메모

- 학습 캘린더의 카테고리가 전부 "프로젝트/회고"라 별도 논문 트랙이 없어, **프로젝트(멀티홉 Agentic RAG) 진행 상황을 학습 주제로 간주**하고 추천했습니다.
- "논문 정리 DB"는 조회 권한 문제로 접근하지 못해 **기존에 읽은 논문과의 중복 여부는 확인하지 못했습니다.** ReAct / SELF-RAG / HotpotQA / RAG Best Practices는 검색 결과상 이미 정리하신 것으로 보여 후보에서 제외했습니다.
- 한글 해설은 세 논문 모두 개별 논문 리뷰 글이 아직 없어, **주제(Agentic RAG / 리랭커 / RAGAS) 단위의 한글 자료**로 대체했습니다.
- 페이지 수는 3번만 arXiv 메타데이터로 확정(6p) 확인했고, 1·2번은 본문 기준 추정치입니다.
