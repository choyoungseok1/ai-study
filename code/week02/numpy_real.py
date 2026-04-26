import numpy as np

#1. 5×5 랜덤 정수 배열(1~100) 만들고, 각 행의 최대값만 뽑아서 1차원 배열로 출력
rand55 = np.random.randint(1,100,size = (5,5))
print(rand55)
print([max(rand55[i]) for i in range(len(rand55))])

#1~50 배열에서 3의 배수이면서 5의 배수가 아닌 수만 필터링
arr1to50 = np.array([i for i in range(1,51) if i % 3==0 and i%5 != 0])
print(arr1to50)
#4×4 배열 두 개 만들어서 행렬 곱(dot product) 계산
arr1 = np.random.randint(1,10,size = (4,4))
arr2 = np.random.randint(1,10,size = (4,4))

print(arr1@arr2)

#10×10 랜덤 배열에서 평균보다 큰 값은 1, 작거나 같은 값은 0으로 바꾸기

arr1010 = np.random.rand(10,10)


#학생 5명의 국영수 점수(3×5 배열) 만들고, 학생별 평균과 과목별 평균 각각 구하기 (axis 활용)
grade5student = np.random.randint(1,100,size = (3,5))
averagestudent = np.average(grade5student, axis = 0)
averageclass = np.average(grade5student, axis = -1)

print(averageclass,averagestudent)