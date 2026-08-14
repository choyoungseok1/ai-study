"""
Gemini OpenAI 호환 엔드포인트 tool calling 검증
확인 지점 3개: ① 스키마 전송 ② tool_calls 파싱 ③ 되붙이기 후 2홉
"""
import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"   # 끝 슬래시 유지
MODEL    = "gemini-3.5-flash-lite"
client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url=BASE_URL)

# 네 프로젝트의 search 스키마와 동일하게
TOOLS = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search Wikipedia paragraphs by query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "search query"}
            },
            "required": ["query"],
        },
    },
}]

# 툴 결과는 하드코딩 — 2홉을 유도하도록 '다음 단서'만 주고 답은 안 줌
FAKE = {
    1: "A Little Time is a song by The Beautiful South. "
       "It features a duet between Dave Hemingway and Briana Corrigan.",
    2: "Briana Corrigan is a singer from Belfast, Northern Ireland.",
}

def main():
    messages = [{
        "role": "user",
        "content": "Which country is the singer who duetted with Dave Hemingway "
                   "on 'A Little Time' from? Use the search tool. "
                   "Search one step at a time."
    }]
    hop = 0

    while hop < 4:
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0,
        )
        msg = resp.choices[0].message
        print(f"\n--- hop {hop} ---")
        print("raw:", json.dumps(msg.model_dump(), ensure_ascii=False)[:600])

        if not msg.tool_calls:
            print("FINAL:", msg.content)
            break

        messages.append(msg)          # ← ③ 원본 그대로 되붙이기가 되는가
        for tc in msg.tool_calls:
            print("  name:", tc.function.name,
                  "| id:", tc.id,
                  "| args type:", type(tc.function.arguments).__name__,
                  "| args:", tc.function.arguments)
            hop += 1
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": FAKE.get(hop, "No results."),
            })

if __name__ == "__main__":
    main()