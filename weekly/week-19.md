# Week 19 회고

> 기간: 2026-04-28 (월) ~ 2026-05-04 (일)

---

## 이번 주 산출물

**커밋 (4건)**
- `f46c8b1` Day 13: Lv0 240문제 완료, Transformer 논문 리뷰
- `47d8030` Day 15: Lv1 5문제 + Matplotlib 기초 (plot, bar, scatter, subplot)
- `f232937` Day 16: Lv1 5문제 + Matplotlib 심화 (타이틀, savefig)
- `797e392` Day 17: Lv1 5문제 + Seaborn 입문 (countplot, heatmap, pairplot)

**프로젝트/학습**
- 프로그래머스 Lv.0 240문제 전체 완료 (마일스톤 달성)
- 프로그래머스 Lv.1 풀이: pg_lv1_001 ~ pg_lv1_011 (5문제 완료)
- Transformer 논문 리뷰 작성 (`papers/2026-05-01-transformer-review.md`) — Attention, Multi-Head, KV Cache, GQA, MLA 정리
- Matplotlib 기초 + 심화 학습 (`matplotlib_base.py`, `matplotlib_deep.py`)
- Seaborn 입문 (`seaborn_base.py`)
- TIL 4일분 작성 (4/30, 5/1, 5/2, 5/3) — 4/28, 4/29는 미작성

---

## 배운 핵심 3가지

1. **Transformer & Attention 메커니즘** — Q·K 내적 → √d 스케일링 → softmax → V 가중합의 흐름을 이해하고, Multi-Head Attention·Causal Masking·Cross-Attention·KV Caching·GQA·MLA까지 최적화 기법의 계보를 정리함. "왜 필요한가"를 중심으로 논문 리뷰를 작성하며 깊이 있는 이해를 확보함
2. **데이터 시각화 기초 (Matplotlib + Seaborn)** — `plot`, `bar`, `scatter`, `subplot` 등 Matplotlib 핵심 API와 `savefig`·타이틀·범례 커스터마이징을 익히고, Seaborn의 `countplot`, `heatmap`, `pairplot`으로 통계적 시각화 입문
3. **알고리즘 패턴의 일반화** — N×N 관계 행렬로 "누가 누구에게" 데이터 표현, `zip(*matrix)` 전치로 열 합 계산, `all()`/`any()` + generator로 조건 판별 한 줄 처리, `seen` set 패턴으로 순서 유지 중복 제거 등 반복 출현하는 패턴을 체화함

---

## 잘한 점

- (직접 작성)

---

## 아쉬운 점

- (직접 작성)

---

## Notion DB 이번 주 완료/스킵 비율

> Notion 연동이 인증되지 않아 자동 집계 불가. TIL 및 커밋 기반 추정치:

| 날짜 | 활동 내용 | 상태 |
|------|-----------|------|
| 4/28 (월) | TIL 미작성, 커밋 없음 | ⏭️ 스킵 추정 |
| 4/29 (화) | TIL 미작성, 커밋 없음 | ⏭️ 스킵 추정 |
| 4/30 (수) | Lv.0 #184 문제 풀이 | ✅ 완료 |
| 5/1 (목) | Transformer 논문 리뷰 + Lv.0 240문제 완료 | ✅ 완료 |
| 5/2 (금) | Matplotlib 기초·심화 + Lv.1 5문제 | ✅ 완료 |
| 5/3 (토) | Lv.1 5문제 + Seaborn 입문 | ✅ 완료 |
| 5/4 (일) | (오늘) | ⏳ 진행 중 |

**추정 완료율: 4/6 (약 67%)** — 4/28~29 이틀 공백 있음. 정확한 비율은 Notion 캘린더 확인 필요

---

## 다음 주 계획

- (Notion DB 다음 주 항목 참고하여 직접 작성)
- 참고: `matplotlib_deep.py` 빈 파일 → 완성 필요
- 참고: Lv.1 문제 풀이 속도 유지 (이번 주 일 평균 2~3문제)
