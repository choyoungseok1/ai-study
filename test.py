from dotenv import load_dotenv, find_dotenv
import os

path = find_dotenv()
print(".env 경로:", repr(path))      # 빈 문자열('')이면 못 찾은 거
print("로드 성공:", load_dotenv())
key = os.getenv("GROQ_API_KEY")
print("키 상태:", "있음" if key else "없음")