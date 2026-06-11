# 이번 주 AI 논문 추천 (Week 7: NLP 입문)

> 현재 학습 주제: 토큰화(BPE, WordPiece), Word2Vec/임베딩, Seq2Seq + Attention, BERT/GPT
> 추천 기준: 15페이지 이내, 코드 공개 우선, 최신 논문

---

## 1. Understanding Transformers and Attention Mechanisms: An Introduction for Applied Mathematicians

- **arxiv**: https://arxiv.org/abs/2604.00965
- **날짜**: 2026년 4월
- **코드**: 없음 (수학적 해설 중심)

**초록**: Transformer의 attention 메커니즘을 수학적으로 명확하게 설명하는 입문 논문. 텍스트가 벡터로 인코딩되는 과정, Multi-Head Attention, KV Caching, Grouped Query Attention, Latent Attention까지 다룸.

**추천 이유**:
1. 현재 Seq2Seq + Attention을 배우는 단계에서 수학적 직관을 잡기에 최적
2. 최신 효율화 기법(KV cache, GQA)까지 한 논문에서 개관 가능
3. 학습 로드맵상 BERT/GPT 이해를 위한 기초 체력을 만들어 줌

---

## 2. LiteToken: Removing Intermediate Merge Residues From BPE Tokenizers

- **arxiv**: https://arxiv.org/abs/2602.04706
- **날짜**: 2026년 2월
- **코드**: 논문 내 알고리즘 상세 기술 (재현 가능)

**초록**: BPE 어휘에서 학습 과정 중 빈번했지만 실제 토큰화 시 거의 출력되지 않는 "잔여 토큰(intermediate merge residues)"을 식별하고 제거하는 방법 제안. 주요 토크나이저의 약 10% 토큰이 잔여 토큰임을 밝힘.

**추천 이유**:
1. 이번 주 학습하는 BPE 토큰화의 내부 동작을 깊이 이해할 수 있음
2. 토큰 수 감소 → 파라미터 절약 → 노이즈 입력 강건성 향상이라는 실용적 흐름 학습
3. 논문이 짧고 알고리즘이 명확해서 직접 구현 연습에 적합

---

## 3. Pretraining Language Models with Subword Regularization: An Empirical Study of BPE Dropout in Low-Resource NLP

- **arxiv**: https://arxiv.org/abs/2605.13436
- **날짜**: 2026년 5월
- **코드**: 실험 재현 코드 포함 (monolingual/bilingual BERT 학습)

**초록**: BPE dropout을 사전학습(pretraining) 단계에서도 적용하면 저자원 언어 NLP 성능이 향상되는지 실증 연구. 영어, 독일어, 프랑스어, 스페인어, 스와힐리어, 이시코사어에서 BERT 모델을 학습하여 XNLI, PAWS-X 등에서 평가.

**추천 이유**:
1. BPE 학습과 BERT 사전학습이 어떻게 상호작용하는지 한 논문에서 배울 수 있음
2. 현재 주차(토큰화 + BERT)의 두 주제를 연결하는 브릿지 역할
3. 실험 설계가 체계적이라 논문 읽기 연습용으로 좋음

---

## 4. LoRA-Drop: Temporal LoRA Decoding for Efficient LLM Inference

- **arxiv**: https://arxiv.org/abs/2601.02569
- **날짜**: 2026년 1월
- **코드**: https://github.com/hosseinbv/LoRA-Drop

**초록**: LLM 디코딩 시 일부 중간 레이어에서 이전 토큰의 hidden state를 재사용하고 저랭크(LoRA) 보정만 적용하는 plug-and-play 추론 프레임워크. 주기적으로 전체 모델을 실행해 드리프트를 방지.

**추천 이유**:
1. Attention + Transformer 구조를 이해한 뒤 "실제 서빙"에서의 효율화를 맛보기에 적합
2. LoRA 개념은 향후 fine-tuning 학습에 필수이므로 미리 감 잡기 좋음
3. GitHub 코드가 공개되어 실험 재현 가능

---

## 5. ML-Embed: Inclusive and Efficient Embeddings for a Multilingual World

- **arxiv**: https://arxiv.org/abs/2605.15081
- **날짜**: 2026년 5월
- **코드**: 모델, 데이터, 코드 전체 공개

**초록**: 텍스트 임베딩의 높은 학습 비용, 좁은 언어 범위, 투명성 부족 문제를 해결하는 프레임워크 "3-Dimensional Matryoshka Learning(3D-ML)" 제안. 140M~8B 파라미터 모델 스위트 제공.

**추천 이유**:
1. Word2Vec에서 시작해 최신 임베딩 모델이 어디까지 왔는지 조감 가능
2. Matryoshka 임베딩 개념을 배우면 향후 RAG, 검색 시스템 이해에 도움
3. 다국어 임베딩이라 한국어 NLP 응용에도 시사점 있음

---

## 참고 한글 해설 자료

- [The Illustrated Transformer 한글 번역](https://nlpinkorean.github.io/illustrated-transformer/) — Attention 메커니즘 시각적 해설
- [트랜스포머를 활용한 자연어 처리 (텐서플로우 블로그)](https://tensorflow.blog/transformer-nlp/) — NLP 전반 한글 교재
- [RAG 논문 리뷰 (한글)](https://kimjy99.github.io/%EB%85%BC%EB%AC%B8%EB%A6%AC%EB%B7%B0/rag/) — Retrieval-Augmented Generation 해설

---

*생성일: 2026-06-01 | 학습 캘린더 Week 7 기준*
