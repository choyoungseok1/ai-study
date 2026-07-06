# Week 28 회고

> 기간: 2026-06-30 ~ 2026-07-06 (TIL 최근 7일 기준)
> Notion 주차: 6/30~7/2 Week 11 마무리, 7/3~7/6 Week 12 시작
> ⚠️ git 산출물(BFS·rerank·Agentic RAG)은 실제로 나왔으나, TIL은 1일분(7/4)만 작성됐고 Notion 상태도 뒤늦게 갱신되지 않아 "실제 진행 > 기록"인 한 주

---

## 이번 주 산출물

**코드 (git 커밋 2건, Day 84·85)**
- `code/week12/x_to_y.py` — Lv2 "x를 y로 만들기". `+n / ×2 / ×3` 세 연산의 최소 횟수를 그래프 최단경로로 보고 `deque` BFS로 구현. `visited`로 중복 폭발 차단, 도달 불가 시 `-1`. (Day 84, 7/4)
- `code/week11/rag_pipeline.ipynb` — 2단계 검색(재정렬) 파이프라인. bi-encoder로 후보를 넓게 뽑고 `CrossEncoder("BAAI/bge-reranker-base")`로 상위만 재정렬 → 생성까지 `rag_pipeline` 하나로 연결. (Day 84, 7/4)
- `code/week11/rag_app.py` — RAG 미니앱 통합. 재정렬 효과 검증용으로 문서 세트를 near-miss/far distractor로 의도 구성. (Day 84, 7/4)
- `code/week11/tool_calling.ipynb` — Groq SDK tool calling 왕복 구현(스키마 정의 → `tool_calls` 수신 → 실행 → `role:"tool"`로 되돌려 2차 호출). (Day 84, 7/4)
- **`code/week09/React+Agentic_RAG.ipynb` · `code/week12/agentic_rag.ipynb` · `rag_app.py` · `rag_pipeline.py`** — Agentic RAG(ReAct 루프) from scratch. tool calling 왕복을 `while` 루프로 확장, system 프롬프트로 검색 강제·한국어·근거 제한. (Day 85, 7/5) ★ 이번 주 최대 산출물

**파인튜닝**
- QLoRA EOS 종료 이슈 해결(`<|im_end|>` 부착으로 출력 종료) + RAG 통합 파이프라인 파일화. (Notion 7/3 완료)

**커밋 / TIL**
- 커밋 2건(Day 84 7/4, Day 85 7/5).
- TIL 1일분(7/4)만 작성 — Day 85(Agentic RAG)는 큰 산출물임에도 TIL 공백.
- ⚠️ 7/4 TIL은 Day 84 코드 기준으로만 정리됐고, 7/5 커밋된 Agentic RAG는 어느 TIL에도 기록되지 않음.

## 배운 핵심 3가지
1. **"최소 단계 = 최단경로 = BFS"라는 판별 기준.** 가중치 없는 그래프에서 최소 연산/거리를 물으면 BFS. `popleft()`(앞)=큐=BFS, `pop()`(뒤)=스택=DFS이며, DFS로 풀면 먼저 파고든 긴 경로를 답으로 오인해 최단 보장이 깨진다. (cf. flood fill은 "크기 다 세기"라 DFS/BFS 무관, 이 문제는 "최소"라 BFS여야만 함.)
2. **BFS의 `visited`는 큐에 넣는 순간 표시.** "처음 도달 = 최단"이므로 재방문은 항상 같거나 더 긴 경로 → 볼 이유가 없다. 꺼낼 때 표시하면 같은 수가 큐에 중복으로 쌓여 지수 폭발(예: x=2,n=2 → 2+2=4, 2×2=4).
3. **bi-encoder(넓게·빠르게) → cross-encoder(정밀 재정렬)의 2단계 절충, 그리고 tool calling의 왕복 구조.** bi는 질문·문서를 따로 임베딩해 빠르지만 상호작용을 못 보고, cross는 함께 넣어 정확하지만 느리다 → "넓게 검색 후 정밀 재정렬"로 속도·정확도를 절충. tool calling은 LLM이 실행을 안 하고 "이 함수를 이 인자로" 요청만 반환 → 실행은 내 코드, 결과를 되돌려 2차 호출해야 답이 나온다. 이 왕복을 `while`로 감으면 Agentic(ReAct) 루프가 된다.

## 잘한 점
- BFS 최단경로 문제를 "최소를 물으면 BFS→popleft" 원칙으로 못박고, `pop()`/`popleft()` 실수를 원인-교정 쌍으로 TIL에 구조화함.
- 2단계 검색(rerank) 파이프라인을 near-miss/far distractor 문서 세트까지 설계해 재정렬 전/후 순서를 눈으로 검증함.
- **Day 85에 Agentic RAG(ReAct 루프)를 from scratch로 구현** — tool calling 왕복을 반복 판단 루프로 확장해, 시그니처 프로젝트 방향(Agentic RAG)의 실전 적합성을 직접 확인함.

## 아쉬운 점
- **Day 85(Agentic RAG) TIL 미작성.** 이번 주 가장 큰 산출물인데 기록이 없어 "무엇을·왜·어떻게"가 코드에만 남음. 마감 전 TIL 점검 필요.
- **Notion 상태 미갱신 반복.** 7/4 "Agentic RAG — tool calling → ReAct" 항목은 git상 Day 85로 실제 구현됐는데 캘린더엔 '시작 전'으로 남음 → 지난주(6/26 QLoRA)와 동일한 어긋남 패턴.
- 7/5 "FastAPI 서빙 맛보기", 7/6 "채용 트래커·시장 분석" 항목은 시작 전(미착수).
- 7/1은 캘린더 항목 자체가 없는 공백일.

## 다음 주 계획
> Notion 학습 캘린더(Week 12) 다음 주 항목 + 이번 주 미완 이월
- **7/7** 논문 1편 (RAG 평가/Agentic RAG 계열) + 리뷰 + Lv2 1문제
- **7/8** 시그니처 프로젝트 주제 좁히기 — 후보 2개로 압축 + Lv2 1문제
- **7/9** 버퍼 + 주간 회고 + 주제 최종 검토
- **이월 필수 (이번 주 미완):** FastAPI 서빙 맛보기(rag_pipeline API, 7/5) · 채용 트래커 업데이트+시장 분석→프로젝트 후보 재평가(7/6) · **Day 85 Agentic RAG TIL 소급 작성** · Notion 7/4 항목 상태 갱신.

---

## Notion DB 이번 주 완료/스킵 비율
> 학습용 캘린더, 기간 2026-06-30 ~ 2026-07-06 (Date 속성 기준)

| 날짜 | 할일 | 주차 | 상태 |
|------|------|------|------|
| 6/30 | 논문 1편 (DoRA 또는 RAG 평가 계열) + 리뷰 + Lv2 | Week 11 | ✅ 완료 |
| 7/2 | 버퍼데이 (Week 11 회고 + 논문) | Week 11 | ✅ 완료 |
| 7/3 | QLoRA EOS 종료 이슈 해결 + rag_pipeline.py 정리 + Lv2 | Week 12 | ✅ 완료 |
| 7/4 | Agentic RAG — tool calling → ReAct 에이전트 확장 + Lv2 | Week 12 | ⬜ 시작 전 |
| 7/5 | 서빙 맛보기 — FastAPI로 rag_pipeline API 엔드포인트 + Lv2 | Week 12 | ⬜ 시작 전 |
| 7/6 | 채용 트래커 업데이트 + 시장 분석 → 프로젝트 후보 재평가 + Lv2 | Week 12 | ⬜ 시작 전 |

- 항목 6건 · **완료 3 / 시작 전(스킵) 3 / 진행 중 0** (7/1은 캘린더 항목 없음)
- **완료율: 50% (3/6)** — 오늘(7/6) 항목 제외 시 **60% (3/5)**
- 참고: 7/4 '시작 전' 항목은 git상 Day 85(Agentic RAG)로 실제 구현됨 → Notion 상태만 갱신하면 실질 완료율은 **67% (4/6)**.

---
> 참고: Notion 학습용 캘린더는 별도 커넥터로 조회함(productivity 플러그인 계열은 이번 실행에서 미인증). SQL/뷰 쿼리는 플랜 제한으로 개별 페이지 조회로 집계함.
> 자동 실행(주간 회고 스케줄)으로 작성됨. 산출물·완료율은 git 로그와 Notion Date 속성을 기준으로 판단함.
