from time import sleep
from scrapy.selector import Selector

import simplejson as json

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from config.GoogleConfig import GoogleConfig
from config import Config as cfg
from data.Google import Google


class GoogleSpider:

    def __init__(self):
        self.driver = cfg.get_driver()
        self.google_config = GoogleConfig()

    ''' Search the Restaurant URL from given search query by calling @scrap_url function
        @:param query: restaurant name to search
        @:param address: restaurant address for verifying the valid restaurant
        @:returns: the home url of the restaurant @None otherwise'''
    def search(self, query, address):
        self.__init__()

        self.query = query
        self.address = address

        google_url = self.scrap_url()

        if google_url:
            print("GOOGLE: Google URL found: " + google_url)
        else:
            print("GOOGLE: Google URL not found")

            return google_url

        # address_arr = self.address.split(" ")
        # # https: // www.google.com / search?q = 안동장
        # # 서울특별시
        # # 동작구
        # # 흑석로
        # print('address_arr: ',address_arr)
        #
        # driver = self.driver
        # driver.get(cfg.query_url["google"] % (self.query +" "+address_arr[0]+" "+address_arr[1]+" "+address_arr[2]))
        #
        # scrapy_selector = Selector(text=driver.page_source)
        #
        # try:
        #     driver.find_element(By.XPATH, self.google_config.get_template()["body"]) \
        #         .is_displayed()
        #
        #     print('Query found')
        #
        # except NoSuchElementException:
        #     print('Query not found')
        #     pass

    def scrap_url(self):
        url_id = ""

        driver = self.driver
        driver.get(cfg.query_url["google"] % (self.query))
        print(str(driver.get(cfg.query_url["google"] % (self.query))))

        #### 웹페이지가 로드되는 한계 시간 설정 : 30초
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, self.google_config.get_search()["list"])))
        except TimeoutException:
            print("Google: No Search Result")

        scrapy_selector = Selector(text=driver.page_source)
        print('scrapy_selector: ', scrapy_selector)
        if cfg.debug:
            print("address: " + self.address)
        search_result = scrapy_selector.css(self.google_config.get_search()["list"])

        for i in range(len(search_result)):
            li_restaurant = search_result[i]

            # 식당 이름 검색 시 나오는 모든 주소
            li_address = li_restaurant.css(
                self.google_config.get_search()["address"]) \
                .extract_first()

            if li_address:
                if cfg.debug:
                    print("li_address: " + li_address)
                li_address_arr = li_address.split(" ")
                print('li_address_arr: ', li_address_arr)
                address_line = str(self.address).split(" ")

                '''Address formatting [City] [District] [Street]'''
                #### 주소 설정
                if (li_address_arr[0] == cfg.seoul_1 or li_address_arr[0] == cfg.seoul_2) and \
                        li_address_arr[1] == address_line[1] and \
                        li_address_arr[2] == address_line[2]:
                    # print("li_address_arr[0] is : " , li_address_arr[0])
                    if cfg.debug:
                        print(li_address_arr)
                        print(address_line)
                    print("Address matched")
                    url_id = li_restaurant.css(self.google_config.get_search()["url_id"]).extract_first()
                    if cfg.debug:
                        print(url_id)
                    break

        driver.close()
        driver.quit()
        return url_id

    def scrap_restaurant(self, google_url):
        self.__init__()
        self.scrap_google_restaurant(google_url)

    def scrap_google_restaurant(self, google_url):

        driver = self.driver

        print("google_url: "+google_url)

        driver.get(google_url)
        driver.implicitly_wait(3)

        name = self.query
        address = self.address
        cuisine = ""
        try:
            cuisine = driver.find_element_by_xpath(self.google_config.get_template()["cuisine"]).text
        except NoSuchElementException:
            pass

        open_close = ""
        try:
            open_close = driver.find_element_by_class_name(self.google_config.get_template()["open_close"]).text
        except NoSuchElementException:
            pass


        phone = ""
        try:
            phone = driver.find_element_by_css_selector(self.google_config.get_template()["phone"]).text
        except NoSuchElementException:  # spelling error making this code not work as expected
            pass

        website = ""
        try:
            website = driver.find_element_by_css_selector(self.google_config.get_template()["website"]).get_attribute("href")
        except NoSuchElementException:  # spelling error making this code not work as expected
            pass

        location_detail = ""
        try:
            location_detail = driver.find_element_by_class_name(self.google_config.get_template()["location_detail"]).text

        except NoSuchElementException:
            pass

        facilities = ""
        try :
            facilities = driver.find_element_by_class_name(self.google_config.get_template()["facilities"]).text
        except NoSuchElementException:
            pass

        tags = []
        try:
            for i in range(len(driver.find_elements_by_class_name(self.google_config.get_template()["tags"]))):
                tag = driver.find_elements_by_class_name(self.google_config.get_template()["tags"])[i].text
                tags.append(tag)

        except NoSuchElementException:
            pass

        introduce = ""
        try :
            introduce = driver.find_element_by_class_name(self.google_config.get_template()["introduce"]).text
        except NoSuchElementException:
            pass


        rating = ""
        try:
            rating = driver.find_element_by_css_selector(self.google_config.get_template()["rating"]).text
        except NoSuchElementException:  # spelling error making this code not work as expected
            pass

        # if rating:
        #     rating = extract_number(rating)

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

        google = Google(self._id, name, phone, address, cuisine, open_close, rating, google_url, menus, reviews)
        encoded_data = json.dumps(google.__dict__, ensure_ascii=False, encoding="utf-8")
        print(encoded_data)

        if(cfg.data_streaming):
            KafkaProducer.connect_kafka_producer()
        else:
            google.store_data(encoded_data)


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
                driver.find_element(By.CSS_SELECTOR, self.google_config.get_menu()["load_more_stop_btn"]) \
                    .is_displayed()
                break
            except NoSuchElementException:
                try:
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, self.google_config.get_menu()["load_more_btn"]))).click()
                    # print("Click: " + str(i))
                    # i = i + 1
                    # print("KAKAO: Load more menus button clicked")

                except TimeoutException:
                    break

        scrapy_selector = Selector(text=driver.page_source)
        menus = scrapy_selector.css(self.google_config.get_template()["menus"])
        print('len(menus): ', len(menus))

        for i in range(len(menus)):
            menu_dic = {}
            menu = menus[i]
            menu_title = menu.xpath(self.google_config.get_menu()["title"]).extract_first()
            menu_price = menu.xpath(self.google_config.get_menu()["price"]).extract_first()

            if menu_title and menu_price:
                # print("menu_title: " + menu_title)
                # print("menu_price: " + menu_price)
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
            reviews = scrapy_selector.css(self.google_config.get_template()["reviews"])

            for i in range(len(reviews)):
                review_dic = {}
                review = reviews[i]
                review_rating = review.xpath(self.google_config.get_review()["rating"]).extract_first()
                review_text = review.xpath(self.google_config.get_review()["review"]).extract_first()
                reviewer = review.xpath(self.google_config.get_review()["reviewer"]).extract_first()
                review_date = review.xpath(self.google_config.get_review()["review_date"]).extract_first()

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
                if driver.find_element(By.XPATH, (self.google_config.get_review()["load_more_btn"] % str(page_no))) \
                        .is_displayed():
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, self.google_config.get_review()["load_more_btn"] % str(page_no)))).click()
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
                driver.find_element(By.XPATH, self.google_config.get_blog_review()["load_more_stop_btn"]) \
                    .is_displayed()
                if cfg.debug:
                    print("No more Load more reviews button to be clicked")
                break
            except NoSuchElementException:
                try:
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, self.google_config.get_blog_review()["load_more_btn"]))).click()

                    if cfg.debug:
                        print("Load more reviews button clicked")
                        print("Click: " + str(i))
                    i = i + 1

                except TimeoutException:
                    break

        scrapy_selector = Selector(text=driver.page_source)
        blog_reviews = scrapy_selector.css(self.google_config.get_template()["blog_reviews"])

        for i in range(len(blog_reviews)):
            blog_review_dic = {}
            blog_review = blog_reviews[i]
            link = blog_review.xpath(self.google_config.get_blog_review()["link"]).extract_first()
            blog_review_dic["link"] = link
            blog_review_list.append(blog_review_dic)

        print("Blog reviews scraped: " + str(len(blog_review_list)))
        reviews_dic["blog_reviews"] = blog_review_list

        return reviews_dic