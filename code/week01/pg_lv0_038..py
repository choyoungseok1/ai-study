# 문제 설명
# 두 정수 a, d와 길이가 n인 boolean 배열 included가 주어집니다. 첫째항이 a, 공차가 d인 등차수열에서 included[i]가 i + 1항을 의미할 때, 이 등차수열의 1항부터 n항까지 included가 true인 항들만 더한 값을 return 하는 solution 함수를 작성해 주세요.

# 제한사항
# 1 ≤ a ≤ 100
# 1 ≤ d ≤ 100
# 1 ≤ included의 길이 ≤ 100
# included에는 true가 적어도 하나 존재합니다.


#나의 풀이
def solution(a, d, included):
    answer = 0
    for i in range(len(included)):
        if included[i] == True :
            answer += a + i*d
    return answer
#타인의 풀이 1
def solution(a, d, included):

    l = []

    for i, x in enumerate(included):
        if x == True:
            l.append(d*i + a)

    return sum(l)
#이 풀이를 가져온 이유는 enumerate() 때문
#enumerate(): 순서가 있는 자료형에서 인덱스 번호와 값을 동시에 반환하는 함수

