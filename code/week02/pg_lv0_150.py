# 문제 설명
# 어떤 자연수를 제곱했을 때 나오는 정수를 제곱수라고 합니다. 정수 n이 매개변수로 주어질 때, n이 제곱수라면 1을 아니라면 2를 return하도록 solution 함수를 완성해주세요.

# 제한사항
# 1 ≤ n ≤ 1,000,000
#내 코드
def solution(n):
    answer = 0
    if n**(1/2) == int(n**(1/2)):
        answer = 1
    else : answer =2 
    return answer

#남의 코드
def solution(n):
    return 1 if (n ** 0.5).is_integer() else 2

#is_integer(): integer인지 검증하는 함수