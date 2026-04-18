#Jump_to_python 5장


#더하기 기능 구현
# result = 0
# def add(num) : 
#     global result #계산한 값을 계속 유지하기 위해서 전역변수 사용
#     result += num
#     return result

# print(add(3))
# print(add(4))

#이 때 새로이 계산하려 할 경우 새로운 전역변 수 필요
#이걸 해결하기 위해 클래스 사용

class Calculator:
    def __init__(self):
        self.result = 0
        
    def add(self,num):
        self.result += num
        return self.result
    
    def sub(self,num):
        self.result -= num
        return self.result
    
    
cal1 = Calculator()
cal2 = Calculator()     #객체 생성

print(cal1.add(3))
print(cal1.add(5))


class FourCal():
    # def setdata(self,first,second):
    #     self.first = first
    #     self.second = second
    #     #first, second라는 객체 내에서 사용되는 객체변수 생성
    #     #객체는 다른 객체의 영향을 받지 않고 객체변수는 다른 객체의 객체변수의 영향이 없다.
        
    def __init__(self,first,second):
        self.first = first
        self.second = second 
    #생성자는 생성과 동시에 선언되는 것이며 setdata메서드와 동일한 기능이지만 setdata 메서드 없이 first와 second를 같이 선언해줌
        
    def add(self):
        return self.first + self.second
    def sub(self):
        return self.first - self.second
    def mul(self):
        return self.first * self.second
    def div(self):
        return float(self.first / self.second)


a = FourCal(4,2)
# a.setdata(4,2)
print(a.first,a.second)
print(a.add(),a.sub(),a.mul(),a.div())

#상속
class MoreCal(FourCal):
    def pow(self):
        return self.first**self.second
#형태는 class 클래스명(상속할 클래스 명)
#상속할 클래스의 모든 메서드 사용 가능
b=MoreCal(3,1)
print(b.add(),b.sub(),b.mul(),b.div(),b.pow())
# print(a.pow())  여기서는 FourCal에 pow()라는 메서드 없으므로 에러

#메서드 오버라이드
class SafeDiv(FourCal):
    def div(self):
        if self.second == 0:
            return 0
        else :
            return self.first/self.second
        
        
c = SafeDiv(4,0)
print(c.div())
#상속한 클래스의 메서드 중 일부를 수정해서 사용하는 것?


