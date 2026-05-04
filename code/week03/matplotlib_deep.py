#14장
import matplotlib.pyplot as plt
import numpy as np

x = np.arrange(0,2,0.2)

plt.plot(x,x,"bo")
plt.plot(x, x**2, color='#e35f62', marker='*', linewidth=2)
plt.plot(x, x**3, color='forestgreen', marker='^', markersize=9)
plt.tick_params(axis='both', direction='in', length=3, pad=6, labelsize=14)
plt.title('Graph Title') #그래프 제목 설정하기
#tittle(name, loc = , pad = ,fontdict = { ~}) loc과 pad 위치 ㅅㄹ정


plt.show()
#plt.savefig("~.png", dpi = 해상도, facecolor = 배경색,edgecolor = 테두리 색
#   ,bbox_inchies = box의 영역 default or tight, pad_inches= 여백 크기
# ) 그래프 이미지 저장