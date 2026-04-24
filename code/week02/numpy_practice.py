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
print(np.shape(arr))

