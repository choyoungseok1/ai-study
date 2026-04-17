# 영어 알파벳으로 이루어진 문자열 str이 주어집니다. 각 알파벳을 대문자는 소문자로 소문자는 대문자로 변환해서 출력하는 코드를 작성해 보세요.

# 제한사항
# 1 ≤ str의 길이 ≤ 20
# str은 알파벳으로 이루어진 문자열입니다.


str = input()
array = list(str)
result = []
str_result =""
for i in range(len(array)):
    if array[i] == str.upper()[i]:
        result.append(array[i].lower())
    elif array[i] == str.lower()[i]:
        result.append(array[i].upper())
for i in range(len(result)):
    str_result += result[i]
    
    
print(str_result)
    
#여기까지 내가 푼 풀이
#남이 푼 풀이 -1

print(input().swapcase())

#swapcase() 진짜 처음보는 메서드였음;; 충격받음

#남이 푼 풀이2
str = input()
a = ''

for s in str :
    if(s.isupper()) :
        a = a + s.lower()
    else : 
        a = a + s.upper()

print(a)

#문제를 풀면서 isupper()/islower()메서드를 쓸 생각을 못했음 존재를 까먹고있었는데 상기됨


#소감: 단순히 upper/lower만 생각나서 문자를 쪼개서 넣는 것만 생각했는데 몰랐던 함수 + 까먹었던 함수를 기억나게함