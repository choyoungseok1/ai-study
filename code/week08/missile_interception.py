"""
프로그래머스 Lv2 - 미사일 요격 (아이기스 군사 기지 / interval point stabbing)

[문제 요약]
- 폭격 미사일은 x축에 평행한 개구간 (s, e)로 표현된다.
- 요격 미사일은 실수 x좌표에서 y축 방향으로 발사 → 그 x를 '관통하는' 모든 폭격 미사일을 요격.
- 단, 개구간 (s, e)는 s나 e에서 쏘면 못 맞힌다 (양 끝 제외).
- 모든 폭격 미사일을 요격하는 데 필요한 요격 미사일 수의 '최솟값'을 return.

[제한사항]
- 1 ≤ len(targets) ≤ 500,000   → O(n log n) 필요 (완전탐색 / O(n²) DP는 TLE)
- 0 ≤ s < e ≤ 100,000,000

[핵심: 이건 "구간 stabbing" 그리디 문제]
- 본질 = "열린 구간들을 최소 개수의 점으로 전부 찌르기".
- 그리디: e(끝) 기준 오름차순 정렬 → 가장 빨리 끝나는 구간의 '끝 직전'에 점을 찍는다.
  (오른쪽에 찍을수록 뒤에 오는 구간을 더 많이 덮음 → exchange argument로 최적 보장)
- e로 정렬하면 그룹 경계 = 그룹에서 가장 빨리 끝나는 e로 고정.
  새 구간은 e가 더 크니까(정렬), 겹침 판정이 'B.s < cur_end' 하나로 끝.
  (다른 한쪽 'A.s < B.e'는 A.s < cur_end ≤ B.e 라서 자동 참 → 비교 1번 절약)
- 개구간이라 'B.s >= cur_end'면 새 그룹 (점이 끝점에선 못 맞히므로 strict).
"""


def solution(targets):
    missiles = []
    sorted_targets = sorted(targets, key=lambda x: x[1])   # e(끝) 기준 정렬
    for i in range(len(targets)):
        if not missiles:
            missiles.append(sorted_targets[i][1])          # 첫 미사일: 첫 구간의 끝
        else:
            end_curr = missiles[-1]                         # 현재(마지막) 발사한 미사일의 끝
            if end_curr > sorted_targets[i][0]:
                pass                                        # 이미 맞음 (s < cur_end)
            else:
                missiles.append(sorted_targets[i][1])       # 못 맞힘 → 새 미사일

    return len(list(set(missiles)))


# ---------------------------------------------------------------------------
# 피드백 (풀이 과정 회고)
# ---------------------------------------------------------------------------
# [핵심]
#  - dp/완전탐색 X. n ≤ 50만 → O(n²)이면 ~2.5e11 → TLE.
#    정렬 기반 그리디(O(n log n))가 정답. "구간 stabbing"의 정석.
#
# [개념적으로 넘은 고비]
#  1. 값 범위 ≠ 연산 횟수: 좌표가 10^8이어도 복잡도는 '입력 개수 n'에 달림.
#     그리디는 좌표축(0~10^8)을 훑지 않고, 입력에 등장하는 끝점 2n개만 본다.
#     (99,999,999 < 50,000,000 비교나 3 < 5 비교나 똑같이 O(1).)
#  2. 겹침 판정 = (A.s < B.e) AND (B.s < A.e). "한쪽 시작이 다른 쪽 범위 안"이 아님.
#     (반례: A=(5,6), B=(1,10)은 (5,6)에서 겹치지만 B.s=1은 A 범위 밖.)
#     e로 정렬하면 B.e ≥ cur_end라 한 조건이 자동 → 'B.s < cur_end'만 보면 됨.
#  3. "겹친다 = 한 미사일로 묶기"는 함정. 겹쳐도 묶는 게 최적이 아닐 수 있다.
#     (가장 빨리 끝나는 곳에 쏘는 그리디가 최적임이 증명됨.)
#
# [구현하다 잡은 버그 (반복 패턴)]
#  1. 변수 혼동: sorted_targets로 정렬해놓고 비교는 targets[i](원본)로 → 섞인 입력에서 깨짐.
#     → 루프 안에서 전부 sorted_targets[i]로 통일.
#  2. 불필요한 중첩 루프(while / for j): 단일 for + 변수 하나면 충분.
#  3. missiles[0] vs missiles[-1]: 현재 그룹 경계는 '첫' 미사일이 아니라 '마지막' 발사 미사일.
#     (missiles[0]이면 예제에서 5, missiles[-1]로 고치면 3.)
#  4. 반환: 리스트가 아니라 '개수'(len).
#
# [재사용 패턴]
#  - 구간 stabbing: e 정렬 → 가장 빨리 끝나는 곳에 점, s >= cur_end면 새 점.
#  - 정렬이 만든 불변식(e ≥ cur_end)을 써서 겹침 비교를 1번으로 줄인다.
#  - 좌표값이 커도 겁먹지 말 것 — 복잡도는 input size n으로 판단.
#
# [사소한 정리 (선택)]
#  - for i in range(len(targets)) + 인덱싱  →  for s, e in sorted_targets 가 더 깔끔.
#  - return len(list(set(missiles)))  →  올바른 로직이면 끝점이 전부 distinct라
#    len(missiles)만으로 충분 (set / list 불필요).


if __name__ == "__main__":
    print(solution([[1, 4], [4, 5], [4, 8], [3, 8], [5, 12], [10, 14]]))  # 3 (그림 예제)
    print(solution([[7, 9], [1, 5], [2, 6], [4, 8]]))                     # 2 (섞인 입력)
    print(solution([[1, 2], [3, 4], [5, 6]]))                             # 3 (서로 disjoint)
