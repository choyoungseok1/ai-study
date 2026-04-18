# 문제 설명
# 문자열 str이 주어집니다.
# 문자열을 시계방향으로 90도 돌려서 아래 입출력 예와 같이 출력하는 코드를 작성해 보세요.

# 제한사항
# 1 ≤ str의 길이 ≤ 10
#내 코드(최초풀이)
str = input()
for i in range(len(str)):
    print(str[i])
    
#다른 풀이
print("\n".join(input()))

#join함수
#join 함수는  tuple or list만 받을 수 있다고 생각했음.  