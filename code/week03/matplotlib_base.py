#matplottlib 호출
import matplotlib.pyplot as plt

plt.plot([1,2,3,4]) #임의의 개수를 인자로 받는 plot
plt.show()#그래프를 화면에 띄워주는 함수 show

plt.plot([1,2,3,4],[1,4,9,16]) #앞에가 x, 뒤에 y
plt.show()

plt.plot([1,2,3,4],[1,4,9,16],"ro") #ro red o marker plt (x,y,label = "이름")
plt.axis([0,6,0,20]) #axis(xmin,xmax,ymin,ymax)

import numpy as np

t = np.arange(0.,5.,0.2)

plt.plot(t,t,"r--", t, t**2,"bs", t, t**3,"g^") #여러개 동시 호출
plt.show()

#_-------------------- 1장--------------------
#dict 형태도 가능
data_dict = {"data_x":[1,2,3,4,5],"data_y":[2,3,5,10,8]}
plt.plot("data_x","data_y", data = data_dict)


#------------------------2장 ------------------
#축 이름 설정
plt.xlabel("X") #plt.xlabel("X", labelpad = a,fontdict = , loc = ) labelpad는 여백
#fontdict는 font 형태 size,bold 여부 등 결정, loc은 우측 좌측 중앙 위치 지정(ylabel은 상중하)
plt.ylabel("Y")


#---------------------------3장-------------------
plt.legend() #그래프 내 적절한 위치에 범례 legend(loc=) loc은 좌표로 주거나 위치 지정도 가능
# legend(ncol = n ) n은 상수로 범례의 열의 개수 지정
#legend(fontsize= )폰트 사이즈 지정
#legend(frameone = <bool>, shadow = <bool> ) 틀과 그림자 스타일 지정

#-------------------------4장 ----------------------
plt.xlim([0,8]) #x축 범위 [xmin,xmax]
plt.ylim([1,15]) #y축 범위 [ymin,ymax]
#plt.axis("square","scaled" 등등 형태 정하기
#-------------------------5장--------------------


x = np.arange(3)
years = ['2017','2019','2021']
values = [100,400,900]
plt.bar(x,values) #barplot 막대 그래프 color 지정 가능, width = n 옵션으로 넓이 지정도 가능
plt.xticks(x,years) #x에 years 요소 넣기
# ------------------------------------------16장------)

n = 50
np.random.seed(0)

x= np.random.rand(n)
y= np.random.rand(n)

plt.scatter(x,y) #산점도 그리기

#-----------------18장---------------------------------\
    
x1 = np.linspace(0.0, 5.0)
x2 = np.linspace(0.0, 2.0)

y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
y2 = np.cos(2 * np.pi * x2)

plt.subplot(2,1,1) #(row,column,index)
plt.plot(x1, y1, 'o-')
plt.title('1st Graph')
plt.ylabel('Damped oscillation')

plt.subplot(2, 1, 2)                # nrows=2, ncols=1, index=2
plt.plot(x2, y2, '.-')
plt.title('2nd Graph')
plt.xlabel('time (s)')
plt.ylabel('Undamped')

plt.tight_layout()
plt.show()