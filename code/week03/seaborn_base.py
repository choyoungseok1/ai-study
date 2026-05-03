import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 적용
plt.rc('font', family='NanumBarunGothic') 
# 캔버스 사이즈 적용
plt.rcParams["figure.figsize"] = (12, 9)

titanic = sns.load_dataset('titanic')
tips = sns.load_dataset('tips')

sns.set(style='darkgrid')

sns.countplot(x="class",hue = "who", data = titanic) #세로로 그리기
sns.countplot(y= "class", hue = "who",data = titanic) #가로로 그리기
#palette를 써서 색상 팔레트 설정 가능


uniform_data = np.random.rand(10,12)
sns.heatmap(uniform_data, annot = True) #히트맵
#pivot을 활용해서 transpole후 그리는 것도 가능
sns.heatmap(titanic.corr(),annot = True, cmap ="YlGnBu")


sns.pairplot(tips,hue="size") #palette로 적용가능