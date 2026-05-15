# 문제 설명
# 수많은 마라톤 선수들이 마라톤에 참여하였습니다. 단 한 명의 선수를 제외하고는 모든 선수가 마라톤을 완주하였습니다.

# 마라톤에 참여한 선수들의 이름이 담긴 배열 participant와 완주한 선수들의 이름이 담긴 배열 completion이 주어질 때, 완주하지 못한 선수의 이름을 return 하도록 solution 함수를 작성해주세요.

# 제한사항
# 마라톤 경기에 참여한 선수의 수는 1명 이상 100,000명 이하입니다.
# completion의 길이는 participant의 길이보다 1 작습니다.
# 참가자의 이름은 1개 이상 20개 이하의 알파벳 소문자로 이루어져 있습니다.
# 참가자 중에는 동명이인이 있을 수 있습니다.

from collections import Counter
def solution(participant, completion):
    answer = Counter(participant)
    answer.subtract(completion)
    return [k for k, v in answer.items() if v > 0][0]


# 잘한 점:

# 처음에 정렬 방식으로 O(n log n) 접근한 건 좋은 시도였어
# Counter 개념 처음 배우고 바로 적용한 것도 괜찮아

# 못한 점:

# 첫 풀이에서 in + remove 조합이 O(n²)인 걸 몰랐어. 리스트에서 in은 O(n), remove도 O(n)이라는 걸 기억해
# 문제 카테고리가 "해시"인데 정렬로만 접근했어. 카테고리 힌트를 활용하는 습관 들이자

# 새로 배운 것 정리:

# Counter — 빈도수 세기
# Counter.subtract() — 제자리에서 빼기 (새 객체 안 만들어서 빠름)
# 리스트의 in, remove는 O(n) — 대량 데이터에서 쓰면 느려