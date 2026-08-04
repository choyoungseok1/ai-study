"""
llm.py — LLM provider 추상화 (Phase A, W4)

에이전트 루프가 provider SDK 자료형을 직접 만지지 않게 한다.
루프는 ChatResult / ToolCall 만 보고, provider 차이는 어댑터가 흡수한다.

────────────────────────────────────────────────────────────
[왜 이 계층이 필요한가 — 2026-07-31 실측 근거]

Gemini의 OpenAI 호환 엔드포인트로 tool calling을 실제로 돌려본 결과
표준 경로는 **완전히 호환**됐다 (4홉 연속 동작, arguments도 JSON 문자열로 동일).
즉 "호환이 깨진다"는 최초 가설은 틀렸다.

대신 발견한 것: provider 고유 필드가 존재한다.
  Gemini → tool_call 마다 extra_content.google.thought_signature
  Groq/OpenAI → 없음

★ 핵심은 필드가 다르다는 게 아니라 **빠뜨려도 요청이 성공한다**는 것.
  200이 오고 tool call도 나온다. 에러 없이 조용히 품질만 떨어진다.
  → 터지는 고장은 발견되지만, 안 터지는 고장은 배포된다.

그래서 raw 를 들고 다닌다. 어댑터의 역할은 필드를 '버리는' 게 아니라
**원본 보존을 명시적 책임으로 만드는 것**이다.
────────────────────────────────────────────────────────────
"""

import json
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import OpenAI


# ─────────────────────────────────────────────
# [A] 우리 자료형
# ─────────────────────────────────────────────
@dataclass
class ToolCall:
    """provider 무관 tool call 표현."""
    id: str
    name: str
    args: dict          # ★ 이미 파싱됨. 루프가 json.loads 를 몰라도 된다


@dataclass
class ChatResult:
    """provider 무관 응답 표현."""
    text: Optional[str]
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None
    # ★★ raw = SDK 응답의 assistant 메시지 원본. 절대 가공하지 않는다.
    #    되붙일 때 messages.append(result.raw) 로 그대로 쓴다.
    #
    #    왜 model_dump() 가 아닌가:
    #      dict 변환이 extra_content(thought_signature)를 살려낼지
    #      검증되지 않았고, SDK 버전이 바뀌면 조용히 빠질 수 있다.
    #      원본 객체를 그대로 넘기면 그 위험이 없고,
    #      **기존 코드(messages.append(msg))와 같은 객체**라
    #      이번 리팩터가 동작을 안 바꾼다는 게 구조적으로 보장된다.
    #
    #    부가 정보(usage 등)가 필요하면 raw 를 가공하지 말고
    #    ChatResult 에 필드를 따로 추가할 것.


# ─────────────────────────────────────────────
# [B] 어댑터 — OpenAI 호환 엔드포인트
# ─────────────────────────────────────────────
class OpenAICompatProvider:
    """OpenAI 호환 규격을 쓰는 provider (Groq, Gemini, vLLM/EXAONE 등).

    base_url 만 바꾸면 대상이 바뀐다.
    provider 고유 필드는 raw 로 보존된다.
    """

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        # base_url=None 이면 SDK 기본값(OpenAI)
        # ⚠️ Gemini: "https://generativelanguage.googleapis.com/v1beta/openai/"
        #    끝 슬래시 유지. 지우면 404.
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def chat(self, messages, tools=None, **kwargs) -> ChatResult:
        params = {"model": self.model, "messages": messages, **kwargs}
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"      # tools 있을 때만 함께 보낸다

        resp = self.client.chat.completions.create(**params)
        msg = resp.choices[0].message

        tool_calls = []
        for tc in (msg.tool_calls or []):
            tool_calls.append(
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    args=json.loads(tc.function.arguments),
                    # ⚠️ 파싱 실패는 여기서 그대로 던진다 (기존 동작 유지).
                    #    잡아서 args={} 로 넘기거나 error 필드를 두는 안도
                    #    검토했으나, 이번 리팩터의 목표는 '동작을 안 바꾸는 것'
                    #    이라 에러 처리는 범위 밖으로 둔다.
                )
            )

        return ChatResult(text=msg.content, tool_calls=tool_calls, raw=msg)


# ─────────────────────────────────────────────
# [C] 기본 provider — 지연 생성
# ─────────────────────────────────────────────
# ★ import 시점에 만들지 않는다. (2026-08-03 교훈:
#   의존성 주입은 '쓰는 쪽'만 고친 것이고 '만드는 쪽'도 같이 고쳐야 완성된다)
_default = None


def default_provider():
    """배치 평가·노트북용 기본 provider. 처음 필요할 때만 만든다."""
    global _default
    if _default is None:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        _default = OpenAICompatProvider(
            api_key=os.environ["GROQ_API_KEY"],
            model="openai/gpt-oss-120b",
            base_url="https://api.groq.com/openai/v1",
        )
    return _default


# ─────────────────────────────────────────────
# 수동 확인
# ─────────────────────────────────────────────
if __name__ == "__main__":
    p = default_provider()
    r = p.chat([{"role": "user", "content": "Say OK and nothing else."}])
    print("text:", r.text)
    print("tool_calls:", r.tool_calls)
    print("raw type:", type(r.raw).__name__)
