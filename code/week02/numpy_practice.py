import numpy as np

#list와 array의 차이점
mylist1 = [1,2,3]
mylist2 = [4,5,6]
print(mylist1 + mylist2) #[1,2,3,4,5,6] 

myarr1 = np.array(mylist1)
myarr2 = np.array(mylist2)
print(myarr1+myarr2) #[5,7,9]

print(np.ndim(myarr1)) #차원 출력
print(np.shape(myarr1)) #형태 출력(튜플) (3,)

arr= np.array([[1,2,3],[4,5,6]])
print(np.shape(arr)) #(2,3)
arr.dtype # int64
#array 생성시 dtype 지정 가능
arr.size # 6 총 요소 수 
arr.T # transpole

a = np.arange(10) #1~9까지의 array arange(2,10) 2~9 arange(2,10,2) 2,4,6,8
b = np.linspace(1,10,3) # 1~9까지 동일한 길이로 3개

#np.zeros(shape = ()) 0으로 채워진, np.ones(shape = ()) 1로 채워진 np.full(shape = (), fill_values = 채울값) 채울값으로 shape에 맞게 채우기
#np.eye(n) n*n 항등행렬
#np.random.randn(shape) 0~1 랜덤 난수
#indexing은 list와 동일
#np.reshape(n*m) 기존 배열을 n*m 2차원 배열로 바꾸는데 요소 갯수 다르면 error, if n 이나 m 에 -1 쓰면 자동 계산, 형태 저장 x
#리스트와 달리 배열간 연산기호를 쓰면 요소별 계산함 별개로 @는 행렬 곱
#fancy indexing: 인덱스를 리스트로 저장해서 별개로 호출 가능
#np.where(조건, 참일 때 배열, 거짓일 때 배열)


#aixs = 0 행별 =1 열별
#ex) arr.sum(axis = 1) :열별 계산 후 배열로 저장 if 지정 X시 모든 요소의 합

#save("이름", 배열) /// load("이름")   #npy or npz파일