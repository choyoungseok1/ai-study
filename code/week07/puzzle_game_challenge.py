"""
========================================================================
[프로그래머스 Lv2] 퍼즐 게임 챌린지
풀이: 조영석 | Day 54 (2026-06-01)
========================================================================

[문제 설명]
순서대로 n개의 퍼즐을 제한 시간 limit 내에 풀어야 한다.
각 퍼즐은 난이도(diff)와 소요 시간(time_cur)을 가진다.
숙련도(level)에 따라 푸는 데 걸리는 시간이 달라진다.

  - diff <= level : 틀리지 않고 time_cur 만큼 사용해서 해결.
  - diff >  level : 총 (diff - level)번 틀린다.
        틀릴 때마다 time_cur 사용 + 이전 퍼즐을 다시 푸는 time_prev 사용.
        (다시 풀 때는 난이도 무관하게 틀리지 않음)
        다 틀린 뒤 마지막으로 time_cur 사용해서 해결.
    => 걸리는 시간 = (time_cur + time_prev) * (diff - level) + time_cur

목표: 제한 시간 limit 내에 모든 퍼즐을 풀 수 있는 '숙련도의 최솟값'을 return.

제한사항:
  1 <= n <= 300,000
  diffs[0] = 1,  1 <= diffs[i] <= 100,000
  1 <= times[i] <= 10,000
  1 <= limit <= 10^15        <- 매우 크므로 total_time은 int(파이썬은 자동 빅정수)


[핵심 아이디어 — 정답에 대한 이분 탐색]
관찰: 숙련도 level이 높을수록 총 소요 시간은 단조 감소한다.
      (level이 오르면 틀리는 횟수가 줄거나 같으므로 시간이 늘 수 없음)

  level 작음 -> 시간 많이 걸림 -> 실패
  level 큼   -> 시간 적게 걸림 -> 성공

따라서 "성공/실패"가 어떤 경계를 기준으로 딱 나뉜다.
        실패 실패 실패 | 성공 성공 성공
이 경계(성공이 시작되는 최소 level)를 '정답에 대한 이분 탐색'으로 찾는다.

  - level 범위: 1 ~ max(diffs)
    (diff <= level이면 안 틀리므로, level이 max(diffs) 이상이면 무조건 성공.
     그래서 탐색 상한은 max(diffs)로 충분)
  - 각 level이 성공 가능한지 = 전체 소요 시간을 O(n)으로 계산해서 limit 이하인지 체크

시간복잡도: 이분 탐색 O(log(max diff)) x 매번 전체 계산 O(n)
          = O(n log(max diff)) -> n=30만이어도 충분히 통과.
          (단순 완전탐색 level 1~10만 x n = 너무 큼 -> 이분 탐색 필요)
========================================================================
"""


def solution(diffs, times, limit):
    # 이분 탐색 범위: 숙련도는 1 이상, max(diffs) 이상이면 무조건 성공
    left = 1
    right = max(diffs)
    answer = right  # 최악의 경우(가장 높은 숙련도)로 초기화

    while left <= right:
        mid = (left + right) // 2  # 현재 테스트할 숙련도(level)

        total_time = 0
        possible = True

        for i in range(len(diffs)):
            diff = diffs[i]
            time_cur = times[i]
            time_prev = times[i - 1] if i > 0 else 0  # 첫 퍼즐은 이전이 없음

            if diff <= mid:
                # 숙련도 충분 -> 틀리지 않고 통과
                total_time += time_cur
            else:
                # 숙련도 부족 -> (diff - mid)번 틀림
                wrong_count = diff - mid
                total_time += (time_cur + time_prev) * wrong_count + time_cur

            # 이미 제한 시간 초과면 더 볼 필요 없음 (가지치기)
            if total_time > limit:
                possible = False
                break

        if possible:
            # 이 숙련도로 성공 -> 더 낮은 숙련도도 되는지 탐색 (왼쪽으로)
            answer = mid
            right = mid - 1
        else:
            # 제한 시간 초과 -> 숙련도를 더 높여야 함 (오른쪽으로)
            left = mid + 1

    return answer


# ── 직접 검증용 (제출 시 지워도 됨) ──
if __name__ == "__main__":
    # diff=3, time_cur=2, time_prev=4 예시를 단순 확장한 형태로 동작 확인
    # (정확한 공식 예제 테스트케이스가 있으면 그걸로 교체)
    print(solution([1, 3], [4, 2], 14))  # 두 번째 퍼즐 diff=3, time=2, prev=4
