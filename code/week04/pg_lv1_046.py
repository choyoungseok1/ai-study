# 문제 설명
# 정수 배열 numbers가 주어집니다. numbers에서 서로 다른 인덱스에 있는 두 개의 수를 뽑아 더해서 만들 수 있는 모든 수를 배열에 오름차순으로 담아 return 하도록 solution 함수를 완성해주세요.

# 제한사항
# numbers의 길이는 2 이상 100 이하입니다.
# numbers의 모든 수는 0 이상 100 이하입니다.
# 입출력 예
# numbers	result
# [2,1,3,4,1]	[2,3,4,5,6,7]
# [5,0,2,7]	[2,5,7,9,12]


def solution(numbers):
    answer = []
    for i in range(len(numbers)-1):
        for j in range(i+1,len(numbers)):
            answer.append(numbers[i]+numbers[j])
    answer =sorted(set(answer))
    return list(answer)


# 잘한 점:

# range(i+1, len(numbers))로 중복 쌍 방지한 건 정확해
# set으로 중복 값 제거 발상도 좋았어

# 못한 점:

# 정렬 빠뜨린 거. 문제에서 "오름차순"이라고 명시했는데 놓침 — 문제 조건을 끝까지 체크하는 습관 필요
# set → list 변환 시 순서 보장 안 되는 걸 몰랐던 건 자료구조 이해 부족. set은 순서 없다는 걸 확실히 새기자

# 실수 패턴 추가할 만한 것: "출력 조건(정렬, 형식) 마지막에 다시 확인하기"