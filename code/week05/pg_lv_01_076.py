# 문제 설명
# 1부터 입력받은 숫자 n 사이에 있는 소수의 개수를 반환하는 함수, solution을 만들어 보세요.

# 소수는 1과 자기 자신으로만 나누어지는 수를 의미합니다.
# (1은 소수가 아닙니다.)

# 제한 조건
# n은 2이상 1000000이하의 자연수입니다.


def solution(n):
    # 0부터 n까지의 숫자를 소수로 가정하고 True로 초기화
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False  # 0과 1은 소수가 아님
    
    # n의 제곱근까지만 확인하면 됨
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            # i가 소수라면, i의 배수들은 모두 소수가 아님
            # i*i 이전의 배수들은 이미 이전 단계에서 처리되었으므로 i*i부터 시작
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
                
    # True의 개수(소수의 개수)를 합산하여 반환
    return sum(is_prime)