from datetime import datetime
import json
from json import JSONEncoder
import pandas as pd
import json


class Kakao:

    # def __init__(self, _id, rest_name, phone_no, address, cuisine, open_close,
    #              website, location_detail, facilities, rating, url, menus, reviews):
    #     self.source = "KAKAO"
    #     self._id = _id
    #     self.rest_name = rest_name
    #     self.phone_no = phone_no
    #     self.address = address
    #     self.cuisine = cuisine
    #     self.open_close = open_close
    #     self.website = website
    #     self.location_detail = location_detail
    #     self.facilities = facilities
    #     self.rating = rating
    #     self.url = url
    #     self.last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    #     self.menus = menus
    #     if "user_reviews" in reviews:
    #         self.reviews = reviews["user_reviews"]
    #     if "blog_reviews" in reviews:
    #         self.blog_reviews = reviews["blog_reviews"]


    def __init__(self, id, name, address, district, lat_long, phone,  cuisine1, cuisine2,
                 website,  facility,  tag, introduce, rating,  img_url, kakao_url, menus, reviews):
        self.source = "KAKAO"
        self.id = id
        self.name = name
        self.district = district
        self.lat_long = lat_long
        self.phone = phone
        self.address = address
        self.cuisine1 = cuisine1
        self.cuisine2 = cuisine2
        self.website = website
        self.facility = facility
        self.tag = tag
        self.introduce = introduce
        self.rating = rating
        self.img_url = img_url
        self.kakao_url = kakao_url
        self.last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.menus = menus
        if "user_reviews" in reviews:
            self.reviews = reviews["user_reviews"]
        if "blog_reviews" in reviews:
            self.blog_reviews = reviews["blog_reviews"]

    def store_data(self, obj):
        with open('data//kakao.txt', 'a+', encoding='utf-8') as f:
            f.write(obj + ',' + '\n' )


