# from selenium import webdriver
# from tqdm import tqdm
# import time
# import pandas as pd
# import json
#
# driver_path = '/home/haewon/chromedriver'
# driver = webdriver.Chrome(driver_path)
#
# def get_store_names(url):
#
#     href_lists = []
#
#     for n in tqdm(range(1, 11)):
#         driver.get(url.format(n))
#
#         href_a = driver.find_elements_by_css_selector(
#             'body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li:nth-child(n) > div:nth-child(1) > figure > figcaption > div > a')
#         href_b = driver.find_elements_by_css_selector(
#             'body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li:nth-child(n) > div:nth-child(2) > figure > figcaption > div > a')
#         del href_a[10:]
#         del href_b[10:]
#         hrefs = href_a + href_b
#
#         n += 1
#
#         # 식당 하나의 url
#         for j in range(len(hrefs)):
#             href_lists.append(hrefs[j].get_attribute('href'))
#     return href_lists
#
# def stores_csv(href_lists, file_name):
#     stores_lists = []
#     branch_lists = []
#     address_lists_doro = []
#     address_lists_jibun = []
#
#     for i in tqdm(range(len(href_lists))):
#         driver.get(href_lists[i])
#
#         time.sleep(1)
#
#         store_name = driver.find_element_by_class_name('restaurant_name').text
#         branch = driver.find_element_by_class_name('branch').text
#         address_doro = driver.find_element_by_xpath(
#             '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n지번')[0]
#         address_jibun = driver.find_element_by_xpath(
#             '/html/body/main/article/div[1]/div[1]/div/section[1]/table/tbody/tr[1]/td').text.split('\n지번')[1]
#
#         stores_lists.append(store_name)
#         branch_lists.append(branch)
#         address_lists_doro.append(address_doro)
#         address_lists_jibun.append(address_jibun)
#         i += 1
#
#     upso = pd.DataFrame(
#         {
#             '업종명': None,
#             '인허가일자': None,
#             '업소명': stores_lists,
#             '소재지(도로명)': address_lists_doro,
#             '소재지(지번)': address_lists_jibun,
#             '영업장면적': None,
#             '소재지전화': None,
#             '업태명': None
#         }
#     )
#
#     upso.to_csv('/home/haewon/바탕화면/Crawler_복제본/ERCLab Crawler/dataForCrawler/{}.csv'.format(file_name), index=False, encoding='utf-8')
#
# # url : 망고플레이트에서 '경상북도 김천' 검색
# url = 'https://www.mangoplate.com/search/%EA%B2%BD%EC%83%81%EB%B6%81%EB%8F%84%20%EA%B9%80%EC%B2%9C?keyword=%EA%B2%BD%EC%83%81%EB%B6%81%EB%8F%84%20%EA%B9%80%EC%B2%9C&page={}'
# href_lists = get_store_names(url)
# stores_csv(href_lists, 'Gimcheon_0817') # 저장할 파일이름
