from time import sleep
from pprint import pprint

import simplejson as json

from scrapy.selector import Selector

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import googlemaps

from config.KakaoConfig import KakaoConfig
from config import Config as cfg
from data.Kakao import Kakao
# from pipeline import KafkaProducer
# from utlity import extract_number


class KakaoSpider:

    def __init__(self):
        self.driver = cfg.get_driver()
        self.kakao_config = KakaoConfig()

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

        kakao_url = self.scrap_url()

        if kakao_url:
            print("KAKAO: Kakao URL found: " + kakao_url)
        else:
            print("KAKAO: Kakao URL not found")

        return kakao_url

    ''' Scrap the Restaurant URL from searching result
        @:returns: the ID of the restaurant @None otherwise'''

    # 1. 드라이버 로드
    # 2. 식당 검색
    # 3. 주소와 매치 -> 상세페이지 로드
    def scrap_url(self):
        url_id = ""

        driver = self.driver
        driver.get(cfg.query_url["kakao"] % (self.query))
        print(str(driver.get(cfg.query_url["kakao"] % (self.query))))

        #### 웹페이지가 로드되는 한계 시간 설정 : 30초
        try:
            WebDriverWait(driver, 35).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, self.kakao_config.get_search()["list"])))
        except TimeoutException:
            print("KAKAO: No Search Result")

        scrapy_selector = Selector(text=driver.page_source)
        print('scrapy_selector: ',scrapy_selector)
        if cfg.debug:
            print("address: " + self.address)
        search_result = scrapy_selector.css(self.kakao_config.get_search()["list"])

        for i in range(len(search_result)):
            li_restaurant = search_result[i]


            # 식당 이름 검색 시 나오는 모든 주소
            li_address = li_restaurant.css(
                self.kakao_config.get_search()["address"]) \
                .extract_first()


            if li_address:
                if cfg.debug:
                    print("li_address: " + li_address)
                li_address_arr = li_address.split(" ")
                print('li_address_arr: ', li_address_arr)
                address_line = str(self.address).split(" ")


                '''Address formatting [City] [District] [Street]'''
                #### 검색할 주소 설정 필요 : 현재 경상북도 (Config.py 에서 확인)
                if (li_address_arr[0] == cfg.g_north_1 or li_address_arr[0] == cfg.g_north_2) and \
                        li_address_arr[1] == address_line[1] and \
                        li_address_arr[2] == address_line[2]:
                    # print("li_address_arr[0] is : " , li_address_arr[0])
                    if cfg.debug:
                        print(li_address_arr)
                        print(address_line)
                    print("Address matched")
                    url_id = li_restaurant.css(self.kakao_config.get_search()["url_id"]).extract_first()
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

    def scrap_restaurant(self, kakao_url):
        self.__init__()
        self.scrap_kakao_restaurant(kakao_url)


    ''' Scrap the Restaurant home page from the restaurant URL
            @:param kakao_url: URL of the restaurant home page'''

    def scrap_kakao_restaurant(self, kakao_url):


        API_KEY = '' #### 구글 API KEY 입력
        gmaps = googlemaps.Client(key=API_KEY)

        driver = self.driver

        print("kakao_url: "+kakao_url)

        driver.get(kakao_url)
        driver.implicitly_wait(3)

        name = self.query
        address = self.address
        district = [self.address.split(' ')[2]]
        geocode_result = gmaps.geocode(address)
        lat_long = f"{geocode_result[0]['geometry']['location']['lat']},{geocode_result[0]['geometry']['location']['lng']}"

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
        try:
            cuisine2 = driver.find_element_by_class_name('txt_location').text.split(',')
            # cuisine_obj = driver.find_element_by_xpath(self.kakao_config.get_template()["cuisine"]).text
            # cuisine.append(cuisine_obj)
        except NoSuchElementException:
            cuisine2 = []

        cuisine1 = None
        try:
            if cuisine2 in korean_cuisine:
                cuisine1=['한식']
                if cuisine2 == ['한식']:
                    cuisine2 = []
            elif cuisine2 in chinese_cuisine:
                cuisine1=['중식']
                if cuisine2 ==['중식']:
                    cuisine1 = []
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


        # open_close = ""
        # try:
        #     open_close = driver.find_element_by_class_name(self.kakao_config.get_template()["open_close"]).text
        # except NoSuchElementException:
        #     pass


        phone = ""
        try:
            phone = driver.find_element_by_css_selector(self.kakao_config.get_template()["phone"]).text
        except NoSuchElementException:  # spelling error making this code not work as expected
            pass

        website = ""
        try:
            website = driver.find_element_by_css_selector(self.kakao_config.get_template()["website"]).get_attribute("href")
        except NoSuchElementException:  # spelling error making this code not work as expected
            pass

        # location_detail = ""
        # try:
        #     location_detail = driver.find_element_by_class_name(self.kakao_config.get_template()["location_detail"]).text
        #
        # except NoSuchElementException:
        #     pass



        facility = None
        try :
            facility = driver.find_element_by_class_name(self.kakao_config.get_template()["facilities"]).text.replace('\n',',').split(',')

            # facilities.append(facilities_obj)
        except NoSuchElementException:
            facility = []




        tag = []
        try:
            for i in range(len(driver.find_elements_by_class_name(self.kakao_config.get_template()["tags"]))):
                tag_obj = driver.find_elements_by_class_name(self.kakao_config.get_template()["tags"])[i].text.replace('#','')
                tag.append(tag_obj)
        except NoSuchElementException:
            tag = []
            pass

        introduce = ""
        try :
            introduce = driver.find_element_by_class_name(self.kakao_config.get_template()["introduce"]).text
        except NoSuchElementException:
            pass



        rating = None
        try:
            rating = float(driver.find_element_by_css_selector(self.kakao_config.get_template()["rating"]).text.replace('점',''))
        except :  # spelling error making this code not work as expected
            pass

        img_url = ""
        try:
            img_url = driver.find_elements_by_class_name('link_photo')[0].get_attribute('style')[25:-3]
        except :
            img_url = "http://www.newdesignfile.com/postpic/2015/02/funny-no-image-available-icon_68017.jpg"



        if cfg.debug:
            print("ID: " + self._id)
            print("name: " + name)
            print("address: " + address)
            print("cuisine: " + cuisine)
            print("phone: " + phone)
            print("website: " + website)
            print("rating: " + rating)

        menus = self.scrap_menus(driver)
        print("Menus scraped: " + str(len(menus)))
        # pprint(menus)

        reviews = self.scrap_reviews(driver)
        # pprint(reviews)

        kakao = Kakao(self.id, name, address, district, lat_long, phone,  cuisine1, cuisine2,  website, facility,
                      tag, introduce, rating,  img_url, kakao_url, menus, reviews)
        encoded_data = json.dumps(kakao.__dict__, ensure_ascii=False, encoding="utf-8")
        print(encoded_data)

        # Kafka pipeline
        if(cfg.data_streaming):
            KafkaProducer.connect_kafka_producer()
        else:
            kakao.store_data(encoded_data)


        driver.close()
        driver.quit()


    ''' Scrap the Restaurant Menu list
        @:param driver: HTML dynamic page content extracted by @Selenium driver
        @:param tabs: tabs from the home page'''
    def scrap_menus(self, driver):
        menu_list = []

        i = 1

        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, self.kakao_config.get_menu()["load_more_stop_btn"]) \
                    .is_displayed()
                # print("KAKAO: No more Load more menus button to be clicked")
                break
            except NoSuchElementException:
                try:
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, self.kakao_config.get_menu()["load_more_btn"]))).click()
                    # print("Click: " + str(i))
                    # i = i + 1
                    # print("KAKAO: Load more menus button clicked")

                except TimeoutException:
                    break



        scrapy_selector = Selector(text=driver.page_source)
        menus = scrapy_selector.css(self.kakao_config.get_template()["menus"])
        print('len(menus): ', len(menus))

        for i in range(len(menus)):
            menu_dic = {}
            menu = menus[i]
            # menu_rest_name =
            menu_title = menu.xpath(self.kakao_config.get_menu()["title"]).extract_first()
            try:
                menu_price = int(menu.xpath(self.kakao_config.get_menu()["price"]).extract_first().replace(',',''))
            except:
                menu_price = menu.xpath(self.kakao_config.get_menu()["price"]).extract_first()


            if menu_title and menu_price:
                # print("menu_title: " + menu_title)
                # print("menu_price: " + menu_price)
                # menu_dic["name"] =
                menu_dic["title"] = menu_title
                menu_dic["price"] = menu_price
                menu_list.append(menu_dic)

        return menu_list


    def scrap_reviews(self, driver):
        reviews_dic = {}
        review_list = []
        blog_review_list = []

        page_no = 1
        first_pagination = True
        while True:
            scrapy_selector = Selector(text=driver.page_source)
            reviews = scrapy_selector.css(self.kakao_config.get_template()["reviews"])

            for i in range(len(reviews)):
                review_dic = {}
                review = reviews[i]
                review_rating = review.xpath(self.kakao_config.get_review()["rating"]).extract_first()
                review_text = review.xpath(self.kakao_config.get_review()["review"]).extract_first()
                reviewer = review.xpath(self.kakao_config.get_review()["reviewer"]).extract_first()
                review_date = review.xpath(self.kakao_config.get_review()["review_date"]).extract_first()

                if not review_rating:
                    review_rating = ""

                # add filter to click (more) button fro long text
                if not review_text:
                    review_text = ""

                # remove the last '.' from date string
                if not reviewer:
                    reviewer = ""

                if review_date:
                    review_date = review_date[:-1]

                # print("rating: " + review_rating)
                # print("review: " + review_text)
                # print("reviewer: " + reviewer)
                # print("review_date: " + review_date)
                review_dic["rating"] = review_rating
                review_dic["review"] = review_text
                review_dic["reviewer"] = reviewer
                review_dic["review_date"] = review_date
                review_list.append(review_dic)

            try:
                if driver.find_element(By.XPATH, (self.kakao_config.get_review()["load_more_btn"] % str(page_no))) \
                    .is_displayed():

                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, self.kakao_config.get_review()["load_more_btn"]  % str(page_no)))).click()
                    sleep(1)

                if cfg.debug:
                    print("Load more reviews button clicked")
                    print("Click: " + str(page_no))

                if first_pagination:
                    if page_no == 5:
                        page_no = 2
                        first_pagination = False
                        if cfg.debug:
                            print("First pagination: False")
                    else:
                        page_no = page_no + 1
                else:
                    if page_no == 6:
                        page_no = 2
                    else:
                        page_no = page_no + 1

            except NoSuchElementException:

                '''Add reviews in user review list'''
                reviews_dic["user_reviews"] = review_list

                if cfg.debug:
                    print("No more Load more reviews button to be clicked")
                    print("Click: " + str(page_no))
                break

        print("User reviews scraped: " + str(len(review_list)))
        '''Add reviews in user review list'''
        reviews_dic["user_reviews"] = review_list

        i = 1
        while True:
            try:
                driver.find_element(By.XPATH, self.kakao_config.get_blog_review()["load_more_stop_btn"]) \
                    .is_displayed()
                if cfg.debug:
                    print("No more Load more reviews button to be clicked")
                break
            except NoSuchElementException:
                try:
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, self.kakao_config.get_blog_review()["load_more_btn"]))).click()

                    if cfg.debug:
                        print("Load more reviews button clicked")
                        print("Click: " + str(i))
                    i = i + 1

                except TimeoutException:
                    break



        scrapy_selector = Selector(text=driver.page_source)
        blog_reviews = scrapy_selector.css(self.kakao_config.get_template()["blog_reviews"])

        for i in range(len(blog_reviews)):
            blog_review_dic = {}
            blog_review = blog_reviews[i]
            link = blog_review.xpath(self.kakao_config.get_blog_review()["link"]).extract_first()
            blog_review_dic["link"] = link
            blog_review_list.append(blog_review_dic)

        print("Blog reviews scraped: " + str(len(blog_review_list)))
        reviews_dic["blog_reviews"] = blog_review_list

        return reviews_dic