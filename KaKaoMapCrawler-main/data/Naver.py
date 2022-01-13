from datetime import datetime
import json
from simplejson import JSONEncoder


class Naver:

    def __init__(self, id, name, address, district, lat_long, cuisine1, cuisine2,
                 website, facility,  tag,   rating,  img_url,  naver_url, menus, reviews):
        self.source = "NAVER"
        self.id = id
        self.name = name
        self.address = address
        self.district = district
        self.lat_long = lat_long
        self.cuisine1 = cuisine1
        self.cuisine2 = cuisine2
        self.website = website
        self.facility = facility
        self.tag = tag
        self.rating1 = rating

        self.img_url = img_url
        self.naver_url = naver_url
        self.last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.menus = menus
        if "user_reviews" in reviews:
            self.reviews = reviews["user_reviews"]
        if "blog_reviews" in reviews:
            self.blog_reviews = reviews["blog_reviews"]


    def store_data(self, obj):
        with open('data//naver.txt', 'a+', encoding='utf8') as f:
            f.write(obj+','+'\n')


# class NaverEncoder(JSONEncoder):
#     def default(self, o):
#         return o.__dict__