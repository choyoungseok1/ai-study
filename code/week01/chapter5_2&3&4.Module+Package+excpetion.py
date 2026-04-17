#Module = 함수와 클래스의 집합
#import 모듈명
#from 모듈명 import 함수명
#if __name__ == __main__ ----> 실제 실행시킨 파일이랑 실행시킬 파일이랑 같은지 판단?

#패키지 = 폴더 + __init__.py, from A.B import C로 가져다 쓰기


#오류란? 문법적 또는 구조적으로 코드가 실행 안되는 것 

#예외처리 
#1) try-except
#try: ~ except 오류구문(as 오류변수):

try :
    4/0
except ZeroDivisionError as e:
    print(e)
    
    
#2) try -finally
try:
    4/0
except ZeroDivisionError:
    print("오류발생")
    
#except 추가 가능, 예상되는 오류가 더 있을 시 물론 병렬로 except(errorName1, errorName2): 이런식으로 처리도 가능
finally:
    print("아무튼 실행됨")
    
#3) try else
try:
    age = int(input("나이를 입력하세요:"))
except:
    print("입력이 올바르지 않습니다.")
else :
    if age<19:
        print("미성년자입니다.")
    else :
        print("성인입니다.")
        
        
#때때로 대량의 데이터를 처리할 때 오류를 넘어가야 할 수도 있음 그 떄 사용하는게 pass 또는 continue
#pass는 오류를 완전 무시, continue는 일단 중단은 안시키고 다음 데이터를 처리


# 의도적으로 에러 발생시키기
def set_age(age):
    if age < 0:
        raise ValueError("나이는 음수가 될 수 없습니다")
    print(f"나이: {age}")