# AI 논문 추천 (2026.05.25 주간)

> **현재 학습 현황 (Notion 캘린더 기반):** CNN 심화 / RNN 구현 / PyTorch nn.Module & Autograd / Transformer 비교  
> **선정 기준:** 15페이지 이내, 코드 공개 우선, 현재 학습 주제와 연관성 높은 논문

---

## 1. HAViT: Historical Attention Vision Transformer

- **저자:** Swarnendu Banik, Manish Das, Shiv Ram Dubey, Satish Kumar Singh
- **발표:** 2026년 3월 (arXiv:2603.18585)
- **페이지:** 약 10페이지
- **코드:** [https://github.com/banik-s/HAViT](https://github.com/banik-s/HAViT)

**초록 요약:**  
기존 Vision Transformer(ViT)에서 각 레이어가 독립적으로 attention을 계산하는 한계를 극복하기 위해, 이전 레이어의 attention 행렬을 보존·혼합하는 Historical Attention Propagation 메커니즘을 제안합니다. CIFAR-100에서 75.74% → 77.07%, TinyImageNet에서 57.82% → 59.07%로 정확도를 향상시켰습니다.

**추천 이유:**
1. CNN에서 Transformer로 넘어가는 학습 단계에서, ViT의 attention 메커니즘이 레이어 간 어떻게 작동하는지 깊이 이해할 수 있습니다.
2. 코드가 공개되어 있어 PyTorch로 직접 실험하며 attention 시각화를 해볼 수 있습니다.
3. 논문이 짧고 실험 구성이 명확하여 처음 ViT 논문을 읽는 학습자에게 적합합니다.

**arxiv:** [https://arxiv.org/abs/2603.18585](https://arxiv.org/abs/2603.18585)

**한글 해설 (ViT 기초):**
- [WikiDocs - ViT 해설](https://wikidocs.net/236136)
- [ViT 논문 리뷰 (Velog)](https://velog.io/@choonsik_mom/Vision-TransformerViT-%EB%85%BC%EB%AC%B8-%EB%A6%AC%EB%B7%B0)
- [gaussian37 - ViT 상세 설명](https://gaussian37.github.io/dl-concept-vit/)

---

## 2. Sparser, Faster, Lighter Transformer Language Models

- **저자:** Edoardo Cetin, Stefano Peluchetti 외 (Sakana AI)
- **발표:** 2026년 3월 (arXiv:2603.23198)
- **페이지:** 약 13페이지
- **코드:** [https://github.com/SakanaAI/sparser-faster-llms](https://github.com/SakanaAI/sparser-faster-llms)

**초록 요약:**  
Transformer LLM의 FFN(Feed-Forward Network) 레이어에서 비구조적 희소성(unstructured sparsity)을 활용하여 모델을 경량화합니다. 단순한 L1 정규화만으로 99% 이상의 희소성을 달성하면서도 성능 저하가 거의 없으며, 새로운 sparse packing 포맷과 CUDA 커널을 통해 추론·학습 속도를 크게 개선합니다.

**추천 이유:**
1. CNN에서 배우는 정규화(Regularization) 개념이 Transformer에서 어떻게 확장 적용되는지 볼 수 있습니다.
2. Sakana AI가 코드와 기술 블로그를 모두 공개하여 실습 자료가 풍부합니다.
3. 모델 경량화는 실무에서 매우 중요한 주제로, 향후 프로젝트에 직접 응용할 수 있습니다.

**arxiv:** [https://arxiv.org/abs/2603.23198](https://arxiv.org/abs/2603.23198)  
**기술 블로그:** [https://sakana.ai/twell/](https://sakana.ai/twell/)

**한글 해설 (모델 경량화 기초):**
- [지식 증류 해설 (baeseongsu 블로그)](https://baeseongsu.github.io/posts/knowledge-distillation/)
- [모델 경량화 기법 - Knowledge Distillation (Velog)](https://velog.io/@qtly_u/%EB%AA%A8%EB%8D%B8-%EA%B2%BD%EB%9F%89%ED%99%94-%EA%B8%B0%EB%B2%95-Knowledge-Distillation)

---

## 3. RWKV: Reinventing RNNs for the Transformer Era

- **저자:** Bo Peng 외
- **발표:** 2023년 5월 (arXiv:2305.13048), EMNLP 2023 Findings 채택
- **페이지:** 약 12페이지
- **코드:** [https://github.com/BlinkDL/RWKV-LM](https://github.com/BlinkDL/RWKV-LM)

**초록 요약:**  
RNN의 효율적인 추론과 Transformer의 병렬 학습 장점을 결합한 RWKV 아키텍처를 제안합니다. Linear attention 메커니즘을 활용하여 Transformer처럼 병렬 학습이 가능하면서도, RNN처럼 O(1) 메모리로 추론할 수 있습니다. 14B 파라미터까지 확장하여 비슷한 크기의 Transformer와 동등한 성능을 달성했습니다.

**추천 이유:**
1. 현재 RNN을 학습 중이므로, RNN의 한계와 이를 극복하는 최신 접근법을 동시에 이해할 수 있습니다.
2. RNN ↔ Transformer의 관계를 수학적으로 명쾌하게 설명하여, 두 아키텍처의 본질적 차이를 깊이 파악할 수 있습니다.
3. 활발한 오픈소스 커뮤니티가 있어 다양한 구현 예제와 실험을 따라해볼 수 있습니다.

**arxiv:** [https://arxiv.org/abs/2305.13048](https://arxiv.org/abs/2305.13048)

**한글 해설:**
- [WikiDocs - RWKV 상세 해설](https://wikidocs.net/236059)
- [ITPE JackerLab - RWKV 해설](https://itpe.jackerlab.com/entry/RWKVReceptance-Weighted-Key-Value)

---

## 4. Memory-Efficient Looped Transformer (MELT)

- **저자:** Victor Conchello Vendrell 외
- **발표:** 2026년 5월 (arXiv:2605.07721) — 최신!
- **페이지:** 약 12페이지
- **코드:** 미공개 (논문 내 구현 상세 설명 포함)

**초록 요약:**  
반복적(looped) Transformer에서 추론 깊이가 증가할수록 KV 캐시 메모리가 선형으로 증가하는 문제를 해결합니다. MELT는 레이어당 단일 KV 캐시를 유지하면서 학습 가능한 게이팅 메커니즘으로 업데이트하여, 메모리 사용량을 일정하게 유지하면서도 성능을 보존합니다.

**추천 이유:**
1. 2026년 5월 최신 논문으로, Transformer 아키텍처의 최전선 연구 동향을 파악할 수 있습니다.
2. RNN의 순환 구조와 Transformer의 attention을 결합하는 하이브리드 접근으로, 현재 학습 중인 두 아키텍처를 연결해서 이해할 수 있습니다.
3. KV 캐시, 게이팅 메커니즘 등 핵심 개념을 다루어 딥러닝 내부 동작 이해에 도움이 됩니다.

**arxiv:** [https://arxiv.org/abs/2605.07721](https://arxiv.org/abs/2605.07721)

---

## 5. Evolving Knowledge Distillation for Lightweight Neural Machine Translation

- **저자:** 여러 저자
- **발표:** 2026년 5월 (arXiv:2605.09924) — 최신!
- **페이지:** 약 10페이지
- **코드:** 논문 내 구현 상세 포함

**초록 요약:**  
기존 Knowledge Distillation의 한계를 극복하기 위해, 점진적으로 용량이 증가하는 여러 teacher 모델 시퀀스로부터 student 모델이 학습하는 Evolving Knowledge Distillation(EKD) 프레임워크를 제안합니다. 신경망 기계번역(NMT) 태스크에서 기존 방법 대비 우수한 성능을 보입니다.

**추천 이유:**
1. CNN/RNN에서 배운 모델 구조를 실제로 경량화·배포하는 실무적 관점을 제공합니다.
2. Teacher-Student 프레임워크를 단계별로 설명하여 Knowledge Distillation 입문에 적합합니다.
3. 2026년 5월 최신 논문으로, 모델 압축 분야의 현재 연구 방향을 파악할 수 있습니다.

**arxiv:** [https://arxiv.org/abs/2605.09924](https://arxiv.org/abs/2605.09924)

**한글 해설 (Knowledge Distillation 기초):**
- [지식 증류 개념 정리 (baeseongsu)](https://baeseongsu.github.io/posts/knowledge-distillation/)
- [LLM Knowledge Distillation 훑어보기 (DevOcean)](https://devocean.sk.com/blog/techBoardDetail.do?ID=167285&boardType=techBlog)
- [지식 증류의 모든 것 (TuringPost)](https://turingpost.co.kr/p/topic-30-knowledge-distillation)

---

## 이번 주 추천 읽기 순서

| 순서 | 논문 | 이유 |
|:---:|------|------|
| 1 | RWKV | 현재 RNN 학습과 직결, RNN→Transformer 전환의 핵심 논문 |
| 2 | HAViT | CNN→ViT 확장, attention 메커니즘 심화 이해 |
| 3 | MELT | RNN+Transformer 하이브리드, 최신 연구 동향 파악 |
| 4 | Sparser, Faster, Lighter | 모델 경량화 실무, 정규화 개념 확장 |
| 5 | EKD | Knowledge Distillation 입문 (시간 여유가 있을 때) |

---

*생성일: 2026년 5월 25일 | Notion 학습 캘린더 기반 자동 추천*
