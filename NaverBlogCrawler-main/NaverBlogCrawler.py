import pandas as pd
from selenium import webdriver
import time
from tqdm import tqdm

def run():
    driver = webdriver.Chrome(f'{driver_path}') #### 드라이버 경로 설정



    url = f'https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate={startDate}&endDate={endDate}&keyword={keyword}'
    driver.get(url)

    time.sleep(1)

    search_number = int(
        driver.find_element_by_class_name('search_number').text.replace(',', '').replace('건', ''))  # 총 게시물 수
    hrefs = driver.find_elements_by_class_name('desc_inner')
    url_list = []
    num = 1

    for num in tqdm(range(1, int(search_number / 7))):  # 총 게시물 수/7(한 페이지당 게시물 수)
        for i in range(len(hrefs)):

            try:
                # url 수집 후 리스트에 저장
                time.sleep(0.5)
                href = driver.find_elements_by_class_name('desc_inner')[i].get_attribute('href')
                url_list.append(href)
            except:
                break

        # 다음 페이지로 이동
        num += 1
        driver.get(
            f'https://section.blog.naver.com/Search/Post.naver?pageNo={num}&rangeType=PERIOD&orderBy=sim&startDate={startDate}&endDate={endDate}&keyword={keyword}')

    ### 본문 스크랩

    title_list = []
    writer_list = []
    date_list = []
    text_list = []
    tag_list = []

    for i in tqdm(range(len(url_list))):
        driver.get(url_list[i])
        element = driver.find_element_by_id("mainFrame")  # iframe 태그 엘리먼트 찾기
        driver.switch_to.frame(element)  # 프레임 이동

        title = driver.find_element_by_class_name('pcol1').text  # 제목
        title_list.append(title)
        writer = driver.find_element_by_class_name('nick').text  # 글쓴이
        writer_list.append(writer)
        time.sleep(1)
        try:
            date = driver.find_element_by_class_name('se_publishDate.pcol2').text  # 작성일
            date_list.append(date)
        except:
            date_list.append("NULL")
        try:
            text = driver.find_element_by_class_name('se-main-container').text.replace('\n', ' ')  # 본문
            text_list.append(text)
        except:
            text_list.append("NULL")

        try:
            tags = driver.find_elements_by_class_name('item.pcol2.itemTagfont._setTop')
            tags_dummy = []
            for j in range(len(tags)):
                tag = driver.find_elements_by_class_name('item.pcol2.itemTagfont._setTop')[j].text.replace('#', '')  # 해쉬태그
                tags_dummy.append(tag)
            tag_list.append(tags_dummy)
        except:
            tag_list.append("NULL")

    # print(len(url_list))
    # print(len(title_list))
    # print(len(writer_list))
    # print(len(tag_list))
    # print(len(writer_list))
    # print(len(text_list))

    ##### DataFrame화

    blog = pd.DataFrame(
        {
            "postingId": [num for num in range(len(url_list))],
            "dataSource": "NAVER_BLOG",
            "searchKeyword": f"{keyword}",
            "postingUrl": url_list,
            "title": title_list,
            "author": [writer_list[x].replace('\n', '') for x in range(len(writer_list))],
            "postingDate": date_list,
            "postingText": text_list,
            "hashtags": tag_list
        }
    )

    ##### csv file로 저장
    blog.to_csv(f'{file_path}{file_name}.csv', index=False)

driver_path = '/home/haewon/chromedriver'  ## 드라이버 경로 설정
keyword = '맛집'  ### 검색할 키워드 설정
startDate ='2020-12-01' ### 시작날짜 (검색할 날짜 범위 설정)
endDate = '2021-12-01'  ### 마지막날짜
file_path = '/home/haewon/바탕화면/'  ### 저장할 파일 경로
file_name = 'Posting_맛집' ### 저장할 파일 이름


run()