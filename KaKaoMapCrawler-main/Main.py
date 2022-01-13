#Main.py
#coding: utf-8

from time import sleep
from datetime import datetime

# from Connect import *
# from ElementControl import *
# from Parsing import *
# from DBConnect import *
from Scrapper import Scrapper
from selenium import webdriver
from tqdm import tqdm
import time
import pandas as pd



driver_path = '/home/haewon/chromedriver'
driver = webdriver.Chrome(driver_path)

class Main():
    scrapper = Scrapper()


    def get_store_names(self, query, url):

        href_lists = []

        for n in tqdm(range(1, 2)): # 검색 결과의 1~n-1 페이지
            driver.get(url.format(query, query, n))

            href_a = driver.find_elements_by_css_selector(
                'body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li:nth-child(n) > div:nth-child(1) > figure > figcaption > div > a')
            href_b = driver.find_elements_by_css_selector(
                'body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li:nth-child(n) > div:nth-child(2) > figure > figcaption > div > a')
            del href_a[10:]
            del href_b[10:]
            hrefs = href_a + href_b

            n += 1

            # 식당 하나의 url
            for j in range(len(hrefs)):
                href_lists.append(hrefs[j].get_attribute('href'))
        return href_lists

    def stores_csv(self, href_lists, file_name):
        stores_lists = []
        branch_lists = []
        address_lists_doro = []
        address_lists_jibun = []

        for i in tqdm(range(len(href_lists))):
            driver.get(href_lists[i])

            time.sleep(1)

            store_name = driver.find_element_by_class_name('restaurant_name').text
            branch = driver.find_element_by_class_name('branch').text
            address_doro = driver.find_element_by_xpath(
                '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n지번')[0]
            address_jibun = driver.find_element_by_xpath(
                '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n지번')[1]

            stores_lists.append(store_name)
            branch_lists.append(branch)
            address_lists_doro.append(address_doro)
            address_lists_jibun.append(address_jibun)
            i += 1

        upso = pd.DataFrame(
            {
                '업종명': None,
                '인허가일자': None,
                '업소명': stores_lists,
                '소재지(도로명)': address_lists_doro,
                '소재지(지번)': address_lists_jibun,
                '영업장면적': None,
                '소재지전화': None,
                '업태명': None
            }
        )

        upso.to_csv('{}'.format(file_name), index=False, encoding='utf-8')

    def load_restaurant_file(self):


        print("Current Time =", datetime.now().strftime("%H:%M:%S"))
        df = pd.read_csv("/home/haewon/바탕화면/Crawler/ERCLab Crawler/dataForCralwer/1103test.csv", error_bad_lines=False) ### 파일명 입력

        print('length of file : ', str(len(df)))

        # load_naver(df)
        load_kakao(df)
        # load_google(df)

        print("Current Time =", datetime.now().strftime("%H:%M:%S"))





def load_naver(df):
    for index, row in df.iterrows():
        # if index < 1433 or index == 257:
        #     continue
        print("\n\n ============== Scrapping: " + str(index) + " =============")
        if pd.isnull(row['소재지(도로명)']):
            address = row['소재지(지번)']
        else:
            address = str(row['소재지(도로명)'])

        print("name: " , row['업소명'] , " -address: " , address)
        scrapper.search_naver(str(index), row['업소명'],  address)
        print("Current Time =", datetime.now().strftime("%H:%M:%S"))
        sleep(2)


def load_google(df):
    for index, row in df.iterrows():
        print("\n\n ============== Scrapping: " + str(index) + " =============")
        if pd.isnull(row['소재지(도로명)']):
            address = row['소재지(지번)']
        else:
            address = str(row['소재지(도로명)'])

        # print(str(index), "name: ", row['업소명'], " -address: ", address)
        scrapper.search_google(str(index), row['업소명'], address)

        print("Current Time =", datetime.now().strftime("%H:%M:%S"))
        sleep(2)


def load_kakao(df):
    for index, row in df.iterrows():
        # if index < 1324:
        #     continue
        #
        # if index == 2335:
        #     break
        print("\n\n ============== Scrapping: " + str(index) + " =============")
        if pd.isnull(row['소재지(도로명)']):
            address = row['소재지(지번)']
        else:
            address = str(row['소재지(도로명)'])

        # print("name: " + row['업소명'] + " -address: " + address)
        scrapper.search_kakao(str(index), row['업소명'], address)
        print("Current Time =", datetime.now().strftime("%H:%M:%S"))
        sleep(2)



if __name__ == "__main__":

    # # url : 망고플레이트에서 '직지사' 검색
    query = '직지사'
    url = 'https://www.mangoplate.com/search/{}?keyword={}&page={}'
    href_lists = Main().get_store_names(query, url)

    # 저장할 파일이름
    file_name = '/home/haewon/바탕화면/Crawler/ERCLab Crawler/dataForCralwer/1103test.csv'
    Main().stores_csv(href_lists, file_name)
    driver.close()



    # Hashtag url list
    collect = []
    # 크롤링 시작
    scrapper = Scrapper()
    Main().load_restaurant_file()







