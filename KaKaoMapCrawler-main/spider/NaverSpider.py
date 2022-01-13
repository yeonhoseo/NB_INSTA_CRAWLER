from time import sleep
import time
from pprint import pprint

import simplejson as json

from scrapy.selector import Selector

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import googlemaps

from config.NaverConfig import NaverConfig
from config import Config as cfg
from data.Naver import Naver\
    # , NaverEncoder
# from pipeline import KafkaProducer


class NaverSpider:

    def __init__(self):
        self.driver = cfg.get_driver()
        self.naver_config = NaverConfig()

    def set_id(self, index):
        self.id = index

    ''' Search the Restaurant URL from given search query by calling @scrap_url function
        @:param query: restaurant name to search
        @:param address: restaurant address for verifying the valid restaurant
        @:returns: the home url of the restaurant @None otherwise'''
    def search(self, query, address):
        self.__init__()

        self.query = query
        self.address = address

        naver_url_id = self.scrap_url()

        if naver_url_id:
            print("Naver URL id found: " + naver_url_id)
        else:
            print("Naver URL id not found")

        return naver_url_id

    ''' Scrap the Restaurant URL from searching result
        @:returns: the ID of the restaurant @None otherwise'''


    def scrap_url(self):
        url_id = ""

        driver = self.driver
        driver.get(cfg.query_url["naver"] % (self.query))

        #### 웹페이지가 로드되는 한계 시간 설정 : 30초
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, self.naver_config.get_search()["list"])))
        except TimeoutException:
            print("NAVER: No Search Result")

        scrapy_selector = Selector(text=driver.page_source)
        if cfg.debug:
            print("address: " + self.address)
        search_result = scrapy_selector.css(self.naver_config.get_search()["list"])

        for i in range(len(search_result)):
            li_restaurant = search_result[i]

            # 식당 검색 시에 나오는 모든 주소
            li_address = li_restaurant.xpath(
                self.naver_config.get_search()["address"] % (str(i+1)))\
                .extract_first()

            if cfg.debug:
                print("li_address: " + li_address)


            li_address_arr = li_address.split(" ")
            address_line = self.address.split(" ")
            print('li_address_arr: ',li_address_arr)


            ### 검색할 주소 설정 필요 : 현재 경상북도 (Config.py 에서 확인)
            '''Address formatting [City] [District] [Street]'''
            if (li_address_arr[0] == cfg.g_north_1 or li_address_arr[0] == cfg.g_north_2) and \
                    li_address_arr[1] == address_line[1] and \
                    li_address_arr[2] == address_line[2]:
                if cfg.debug:
                    print(li_address_arr)
                    print(address_line)
                print("Address matched")
                url_id = li_restaurant.css(self.naver_config.get_search()["url_id"]).extract_first()
                if cfg.debug:
                    print(url_id)
                break

        driver.close()
        driver.quit()
        return url_id

    ''' Scrap the Restaurant home page from the restaurant URL or restaurant ID by 
        calling @scrap_naver_restaurant function
        @:param url_id: URL or the ID of the restaurant home page
        @:param url: whether the url_id is a URL or the ID of the restaurant'''
    def scrap_restaurant(self, url_id, url=False):
        self.__init__()

        if url:
            naver_url = url_id
        else:
            naver_url = cfg.detail_page_url["naver"] % (url_id)

        self.scrap_naver_restaurant(naver_url)

    ''' Scrap the Restaurant home page from the restaurant URL
        @:param naver_url: URL of the restaurant home page'''
    def scrap_naver_restaurant(self, naver_url):

        driver = self.driver

        print("naver_url: "+naver_url)

        driver.get(naver_url)

        # tabs = driver.find_elements_by_xpath(self.naver_config.get_template()["tabs"])
        time.sleep(3)
        tabss = driver.find_element_by_class_name('_2MDmw')
        time.sleep(2)
        tabs = tabss.find_elements_by_tag_name('a')

        if cfg.debug:
            print(str(len(tabs)))

        API_KEY = '' #### 구글 API KEY 입력
        gmaps = googlemaps.Client(key=API_KEY)

        name = self.query
        address = self.address
        district = [self.address.split(' ')[2]]
        geocode_result = gmaps.geocode(address)
        lat_long = f"{geocode_result[0]['geometry']['location']['lat']},{geocode_result[0]['geometry']['location']['lng']}"

        ### 음식 종류를 카테고리화 하기 위한 리스트입니다.
        korean_cuisine = [
            ['분식'],
            ['오리'],
            ['두부전문점'],
            ['한정식'],
            ['한식'],
            ['한식뷔페'],
            ['해물', '생선'],
            ['삼계탕'],
            ['냉면'],
            ['불고기', '두루치기'],
            ['매운탕', '해물탕'],
            ['쌈밥'],
            ['순대'],
            ['사철탕', '영양탕'],
            ['곰탕'],
            ['감자탕'],
            ['국수'],
            ['장어'],
            ['해장국'],
            ['굴','전복'],
            ['찌개','전골']
        ]

        chinese_cuisine = [
            ['중화요리'],
            ['양꼬치']
        ]

        japanese_cuisine = [
            ['일식'],
            ['돈까스', '우동'],
            ['초밥', '롤'],
            ['샤브샤브'],
            ['일본식라면']
        ]

        western_cuisine = [
            ['이탈리안'],
            ['패밀리레스토랑'],
            ['피자'],
            ['샌드위치']
        ]

        world_cuisine = [
            ['퓨전요리'],
            ['뷔페'],
            ['동남아음식']
        ]

        drink_cuisine = [
            ['호프', '요리주점'],
            ['술집']
        ]

        meat_cuisine = [
            ['치킨'],
            ['오리'],
            ['육류', '고기'],
            ['불고기', '두루치기'],
            ['곱창', '막창'],
            ['족발', '보쌈'],
            ['닭요리']
        ]

        cafe_cuisine = [
            ['카페'],
            ['커피전문점'],
            ['제과', '베이커리'],
            ['전통찻집'],
            ['떡', '한과'],
            ['디저트카페']
        ]




        cuisine2 = None
        try :
            cuisine2 = driver.find_element_by_class_name('_3ocDE').text.split(',')
        except NoSuchElementException:
            cuisine2 = []

        ### cuisine 1,2 가 중복되지 않도록 설정했습니다.
        cuisine1 = None
        try:
            if cuisine2 in korean_cuisine:
                cuisine1=['한식']
                if cuisine2 == ['한식']:
                    cuisine2 = []
            elif cuisine2 in chinese_cuisine:
                cuisine1=['중식']
                if cuisine2 ==['중식']:
                    cuisine2 = []
            elif cuisine2 in japanese_cuisine:
                cuisine1=['일식']
                if cuisine2 == ['일식']:
                    cuisine2 = []
            elif cuisine2 in western_cuisine:
                cuisine1=['양식']
                if cuisine2 == ['양식']:
                    cuisine2 = []
            elif cuisine2 in world_cuisine:
                cuisine1=['세계음식']
                if cuisine2 == ['세계음식']:
                    cuisine2 = []
            elif cuisine2 in meat_cuisine:
                cuisine1=['육류','고기']
                if cuisine2 == ['육류','고기']:
                    cuisine2 = []
            elif cuisine2 in drink_cuisine:
                cuisine1=['주점']
                if cuisine2 == ['주점']:
                    cuisine2 = []
            elif cuisine2 in cafe_cuisine:
                cuisine1=['카페']
                if cuisine2 == ['카페','베이커리']:
                    cuisine2 = []
        except:
            cuisine1 = ['기타']

        # open_close = "" \
        # try:
        #     open_close =
        # except NoSuchElementException:
        #     pass

        website = ""
        try:
            website = driver.find_element_by_class_name('_2SBb1').find_element_by_tag_name('a').get_attribute('href')
        except NoSuchElementException:
            pass


        facility = None
        try :
            facility = driver.find_element_by_css_selector('#app-root > div > div > div.place_detail_wrapper > div:nth-child(4) > div > div:nth-child(2) > div > ul > li._1M_Iz.undefined > div').text

        except NoSuchElementException:
            facility = []



        tag = []
        tag_lists = driver.find_elements_by_class_name('_3Ryhx')
        print('tag_list: ', tag_lists)

        try:
            if tag_lists == []:
                pass
            else:

                for i in range(len(tag_lists)+1):
                    tag_dic = {}
                    try:
                        tag_mood = tag_lists[0].text
                        if not tag_mood:
                            tag_mood = ""
                        tag_dic['mood'] = tag_mood
                    except:

                        pass

                    try:
                        tag_hot_topic = tag_lists[1].text
                        if not tag_hot_topic:
                            tag_hot_topic = ""
                        tag_dic['hot_topic'] = tag_hot_topic
                    except :

                        pass

                    try:
                        tag_visit_for = tag_lists[2].text
                        if not tag_visit_for:
                            tag_visit_for = ""
                        tag_dic['visit_for'] = tag_visit_for
                    except :

                        pass

                    tag.append(tag_dic)

        except NoSuchElementException:
            tag1 = []
            pass


        rating = None
        try:
            rating = float(driver.find_element_by_class_name('_9bFMx').text.replace('/5',''))
        except:
            pass


        # website = ""
        # try:
        #     website = driver.find_element_by_css_selector(self.naver_config.get_template()["website"]).get_attribute['href']
        # except NoSuchElementException:  # spelling error making this code not work as expected
        #     pass
        if cfg.debug:
            print("ID: " + self._id)
            print("name: "+name)
            print("address: "+address)
            print("website: "+website)

        try:
            menus = self.scrap_menus(driver, tabs)
            print(menus)
            print("Menus scraped: " + str(len(menus)))
        except NoSuchElementException:
            print('Not Found Menus')
            pass
        # print("Menus scraped: "+str(len(menus)))


        if cfg.debug:
            pprint(menus)
        reviews = self.scrap_reviews(driver, tabs)
        if cfg.debug:
            pprint(reviews)

        img_url = self.scrap_img(driver)

        naver = Naver(self.id, name, address, district, lat_long,  cuisine1, cuisine2,  website, facility,  tag,   rating,  img_url,  naver_url, menus, reviews)
        encoded_data = json.dumps(naver.__dict__, ensure_ascii=False, encoding="utf-8")
        print('encoded_data: ', encoded_data)

        if (cfg.data_streaming):
            KafkaProducer.connect_kafka_producer()
        else:
            naver.store_data(encoded_data)

        driver.close()
        driver.quit()


    ''' Scrap the Restaurant Menu list
        @:param driver: HTML dynamic page content extracted by @Selenium driver
        @:param tabs: tabs from the home page'''
    def scrap_menus(self, driver, tabs):
        menu_list = []
        menu_button = ""

        ## tabs  = ['https://m.place.naver.com/restaurant/36652436/home',
                     # 'https://m.place.naver.com/restaurant/36652436/feed',
                     # 'https://m.place.naver.com/restaurant/36652436/menu',  ...]
        ## 끝이 /menu 로 끝나는 요소를 찾아 클릭
        for tab in tabs:
            href_attr = tab.get_attribute("href")
            if href_attr.endswith("/menu"):
                menu_button = tab
                break
        if not isinstance(menu_button, str):
            menu_button.click()
            print('menu button click')

            i = 1
            while True:
                try:
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, self.naver_config.get_menu()["load_more_btn"]))).click()
                    if cfg.debug:
                        print("Load more menus button clicked")
                        print("Click: " + str(i))
                    i = i + 1
                except:
                    if cfg.debug:
                        print("No more Load more menus button to be clicked")
                    break
            print('메뉴 더보기 로드 완료 ')

            # scrapy_selector = Selector(text=driver.page_source)
            # menus = scrapy_selector.css(self.naver_config.get_template()["menus"])
            menus = driver.find_elements_by_class_name('_3j-Cj')

            for i in range(len(menus)):
                menu_dic = {}
                rest_name = driver.find_element_by_class_name('_3XamX').text
                menu_title = driver.find_elements_by_class_name('_3yfZ1')[i].text
                menu_price = driver.find_elements_by_class_name('_3qFuX')[i].text

                if menu_title and menu_price:
                    if cfg.debug:
                        print("menu_title: " + menu_title)
                        print("menu_price: " + menu_price)
                    menu_dic["restaurant"] = rest_name
                    menu_dic["title"] = menu_title
                    menu_dic["price"] = menu_price
                    menu_list.append(menu_dic)

        return menu_list


    def scrap_img(self, driver):
        img_list = []
        photo_button = ""

        time.sleep(3)

        tabs = driver.find_element_by_class_name('_2MDmw').find_elements_by_tag_name('a')

        for tab in tabs:
            href_attr = tab.get_attribute("href")
            if href_attr.endswith("/photo?type=list"):
                photo_button = tab
                break
        if not isinstance(photo_button, str):
            time.sleep(1)
            photo_button.click()
            print('photo button click')

        time.sleep(2)
        try:
            img_obj = driver.find_element_by_class_name('place_thumb').get_attribute('src')
            img_list.append(img_obj)
        except NoSuchElementException:
            pass

        return img_list





    def scrap_reviews(self, driver, tabs):
        reviews_dic = {}
        review_list = []
        blog_review_list = []
        review_button = ""

        sleep(1)
        for tab in tabs:
            try:
                href_attr = tab.get_attribute("href")
                if href_attr.endswith("/review"):
                    review_button = tab
                    break
            except NoSuchElementException:
                print('No reviews tab found')
                return
                pass

        if not isinstance(review_button, str):
            review_button.click()

            count_review_tabs = 0

            try:
                review_tabs = driver.find_elements_by_xpath(self.naver_config.get_template()["review_tabs_len"])
                count_review_tabs = len(review_tabs)
            except NoSuchElementException:  # spelling error making this code not work as expected
                pass

            print('count_review_tabs: '+str(count_review_tabs))
            index_user_reviews = 1
            index_blog_reviews = 2
            if count_review_tabs > 2:
                index_user_reviews = 2
                index_blog_reviews = 3
            print('counting review tabs successfully')

            ### 방문자 리뷰
            review_tab1 = ""
            '''Click First tab and get the User Reviews'''
            try:
                review_tab1 = driver.find_elements_by_class_name("_3Q5_9")[0]
            except :  # spelling error making this code not work as expected
                pass

            if not isinstance(review_tab1, str):

                review_tab1.click()
                print('review tab click')

                i = 1
                while True:
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, self.naver_config.get_review()["load_more_btn"]))).click()
                        print('오키오키')
                        if cfg.debug:
                            print("Load more reviews button clicked")
                            print("Click: " + str(i))
                        i = i + 1
                        sleep(0.5)
                    except TimeoutException:
                        if cfg.debug:
                            print("No more Load more reviews button to be clicked")
                        break
                    except StaleElementReferenceException:
                        if cfg.debug:
                            print("No more Load more reviews button to be clicked")
                        break
            else:
                print("No review buttons...")

            # scrapy_selector = Selector(text=driver.page_source)
            # reviews = scrapy_selector.css(self.naver_config.get_template()["reviews"])
            reviews = driver.find_elements_by_class_name('_1Z_GL')
            # print('reviews: ',reviews)

            i = 0
            for i in range(len(reviews)):
                review_dic = {}
                review = reviews[i]
                time.sleep(2)
                try:
                    review_rating = review.find_element_by_class_name("_2tObC").text
                    time.sleep(3)
                    review_text = review.find_element_by_class_name('WoYOw').text
                except:
                    review_text = ""
                    pass
                reviewer = review.find_element_by_class_name('hbo4A').text
                review_date = review.find_element_by_class_name('ZvQ8X').text
                rest_name = driver.find_element_by_class_name('_3XamX').text

                review_dic['restaurant'] = rest_name


            # for i in range(len(reviews)):
            #     review_dic = {}
            #     review = reviews[i]
            #     review_rating = review.xpath(self.naver_config.get_review()["rating"]).extract_first()
            #     review_text = review.xpath(self.naver_config.get_review()["review"]).extract_first()
            #     reviewer = review.xpath(self.naver_config.get_review()["reviewer"]).extract_first()
            #     review_date = review.xpath(self.naver_config.get_review()["review_date"]).extract_first()

                if review_rating:
                    # have to replace this with extract_number()
                    review_rating = str(int(''.join(filter(str.isdigit, review_rating)))/20)
                else:
                    review_rating = ""

                if not review_text:
                    review_text = ""

                # remove the last '.' from date string
                if not reviewer:
                    reviewer = ""

                if review_date:
                    review_date = review_date[:-1]

                if cfg.debug:
                    print("rating: " + review_rating)
                    print("review: " + review_text)
                    print("reviewer: " + reviewer)
                    print("review_date: " + review_date)
                review_dic["rating"] = review_rating
                review_dic["review"] = review_text
                review_dic["reviewer"] = reviewer
                review_dic["review_date"] = review_date
                review_list.append(review_dic)
                i += 1

            print("User reviews scraped: " + str(len(review_list)))
            '''Add reviews in user review list'''
            reviews_dic["user_reviews"] = review_list

            # #### 블로그 리뷰
            # review_tab2 = ""
            # '''Click First tab and get the User Reviews'''
            # try:
            #     review_tab2 = driver.find_elements_by_class_name("_3Q5_9")[1]
            #
            # except :  # spelling error making this code not work as expected
            #     pass
            #
            # if not isinstance(review_tab2, str):
            #     '''Click Second tab and get the Blog Reviews'''
            #     review_tab2.click()
            #
            #     i = 1
            #     while True:
            #         try:
            #             time.sleep(3)
            #             WebDriverWait(driver, 2).until(
            #                 EC.element_to_be_clickable(
            #                     (By.CSS_SELECTOR, self.naver_config.get_blog_review()["load_more_btn"]))).click()
            #             if cfg.debug:
            #                 print("Load more blog reviews button clicked")
            #                 print("Click: " + str(i))
            #             i = i + 1
            #             sleep(0.5)
            #         except NoSuchElementException:
            #             if cfg.debug:
            #                 print("No more Load more blog reviews button to be clicked")
            #             break
            #         except StaleElementReferenceException:
            #             if cfg.debug:
            #                 print("No more Load more reviews button to be clicked")
            #             break
            #         except:
            #             break
            #
            #     blog_reviews = driver.find_elements_by_class_name(self.naver_config.get_template()["blog_reviews"])
            #     print('Blog_reviews: ',blog_reviews)
            #
            #     i = 0
            #     for i in range(len(blog_reviews)):
            #         blog_review_dic = {}
            #         blog_review = blog_reviews[i]
            #         link = blog_review.find_element_by_class_name('_2HzSL').get_attribute('href')
            #     # for i in range(len(blog_reviews)):
            #     #     blog_review_dic = {}
            #     #     blog_review = blog_reviews[i]
            #     #     link = blog_review.xpath(self.naver_config.get_blog_review()["link"]).extract_first()
            #
            #         blog_review_dic["link"] = link
            #         blog_review_list.append(blog_review_dic)
            #         i += 1
            #
            #     print("Blog reviews scraped: " + str(len(blog_review_list)))
            # reviews_dic["blog_reviews"] = blog_review_list

        return reviews_dic
