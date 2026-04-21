import  requests
from bs4 import BeautifulSoup
#실제 url
url = 'https://kin.naver.com/search/list.nhn?query=%ED%8C%8C%EC%9D%B4%EC%8D%AC'
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("#s_content > div.section > ul > li:nth-child(1) > dl > dt > a")
    print(soup)
else :
    print(response.status_code)
    
#python 검색 시 처음으로 나오는 제목 F12 -> inspector로 크롤릴할 제목 클릭 -> copy as inspector

