"""
프로그래머스 Lv2 - 광물 캐기
https://school.programmers.co.kr/learn/courses/30/lessons/177342

[핵심 아이디어 - 그리디]
- 광물을 순서대로 5개씩 묶으면 한 청크 = 곡괭이 하나가 캐는 단위.
- 실제로 캐는 청크 수 K = min(전체 곡괭이 수, 전체 청크 수).
    · 전체 청크 수 = ceil(len/5)  →  (len + 4) // 5
    · 곡괭이가 모자라면 그만큼만, 광물은 "순서대로" 앞에서부터 캠.
- num_chunk(=K)만큼만 청크를 만들면 "앞에서 K개"가 자동으로 해결됨.
  (광물은 순서대로만 캘 수 있다는 제약을 청크 생성 단계에서 처리)
- 비싼 청크(다이아 많은)에 좋은 곡괭이를 몰아주는 게 최적:
    · 청크를 (다이아 수, 철 수) 내림차순 정렬
    · 정렬된 순서대로 다이아 → 철 → 돌 곡괭이를 배정
- 피로도 표:
    · 다이아 곡괭이: 무엇이든 1            (cost = d + i + s)
    · 철   곡괭이: 다이아 5, 철·돌 1       (cost = 5d + i + s)
    · 돌   곡괭이: 다이아 25, 철 5, 돌 1    (cost = 25d + 5i + s)

[시간복잡도] O(c log c), c = 청크 수(최대 10). 사실상 상수 시간.
"""


def solution(picks, minerals):
    answer = 0
    nm = len(minerals)
    dia, iron, stone = picks[0], picks[1], picks[2]

    # 실제로 캐는 청크 수 = min(곡괭이 총수, 전체 청크 수(올림))
    num_chunk = min(sum(picks), (nm + 4) // 5)

    # 앞에서부터 num_chunk개만 5개씩 묶기 (= 실제 캐는 청크, 순서대로)
    total_chunks = []
    for i in range(num_chunk):
        total_chunks.append(minerals[i * 5:i * 5 + 5])

    # 다이아 많은 청크부터 (동률이면 철 많은 순) → 좋은 곡괭이를 몰아주기 위해
    sort_chunk = sorted(
        total_chunks,
        key=lambda x: (-x.count('diamond'), -x.count('iron'))
    )

    # 청크별 [다이아, 철, 돌] 개수
    num_mineral = []
    for chunk in sort_chunk:
        num_mineral.append([chunk.count("diamond"), chunk.count("iron"), chunk.count("stone")])

    # 정렬된 순서대로 다이아 → 철 → 돌 곡괭이 배정하며 피로도 누적
    count = 0
    while count < len(num_mineral):
        d, i, s = num_mineral[count]
        if dia > 0:
            answer += d + i + s             # 다이아 곡괭이: 전부 1
            dia -= 1
        elif iron > 0:
            answer += 5 * d + i + s          # 철 곡괭이: 다이아만 5
            iron -= 1
        else:
            answer += 25 * d + 5 * i + s     # 돌 곡괭이: 다이아 25, 철 5
            stone -= 1
        count += 1

    return answer


if __name__ == "__main__":
    # 프로그래머스 공식 예제
    tests = [
        (([1, 3, 2],
          ["diamond", "diamond", "diamond", "iron", "iron", "diamond", "iron", "stone"]),
         12),
        (([0, 1, 1],
          ["diamond", "diamond", "diamond", "diamond", "diamond",
           "iron", "iron", "iron", "iron", "iron",
           "diamond", "diamond", "diamond", "diamond", "diamond"]),
         50),
    ]
    all_pass = True
    for idx, ((picks, minerals), expected) in enumerate(tests, 1):
        got = solution(picks, minerals)
        ok = got == expected
        all_pass &= ok
        print(f"test {idx}: {'OK ' if ok else 'FAIL'} | got={got} expected={expected}")
    print("=" * 40)
    print("ALL PASS" if all_pass else "SOME FAILED")


# ============================================================
# 피드백 (Day 67 / 6/13 코테)
# ============================================================
# [잘한 것]
# - 코딩 전에 시간복잡도부터 판단하고 들어갔다 (입력 작으니 완전탐색 OK).
#   그동안 자주 빼먹던 "복잡도 산정 먼저"를 이번엔 제대로 함.
# - 문제 본질(5개 청크 단위 + 곡괭이 배정 최적화)을 정확히 파악.
# - 까다로운 포인트들을 힌트만으로 스스로 풀어냄:
#     · 캐는 청크 수 = min(곡괭이 수, 전체 청크)  — picks 제약을 직접 발견
#     · "다이아 많은 청크에 좋은 곡괭이" 그리디 — 정렬 key (다이아, 철) 내림차순
#     · num_chunk(=K)만큼만 청크 생성 → "순서대로 앞에서 K개"를 우아하게 해결.
#       (이 문제에서 제일 많이 틀리는 부분인데 깔끔하게 넘김)
#
# [고친 것]
# - 청크 수를 처음엔 len//5 + 1 로 잡았다가, 5의 배수일 때 빈 청크가
#   하나 더 생기는 버그를 발견 → 올림인 (len + 4) // 5 로 수정.
#
# [다음에 챙길 것]
# - 변수명: num_mineral 은 "청크별 광물 개수"라 chunk_counts 가 더 명확하고,
#   sort_chunk 는 리스트라 sorted_chunks(복수)가 자연스러움.
# - 제출 전 디버그용 print(num_chunk), print(total_chunks) 는 지우기.
# - else(돌 곡괭이) 분기는 stone > 0 체크가 없지만, num_chunk <= sum(picks)라
#   곡괭이가 항상 충분해서 안전함. (논리는 정확)
