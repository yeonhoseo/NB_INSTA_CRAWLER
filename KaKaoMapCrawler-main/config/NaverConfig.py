import os.path

import yaml
from config import Config as cfg

yaml.warnings({'YAMLLoadWarning': False})

class NaverConfig:

    def __init__(self):

        for filename in os.listdir(cfg.template_path):
            abs_file_path = os.path.abspath("template//naver-site.yaml")
            with open(abs_file_path, 'r') as yaml_file:
                self.naver_site = yaml.load(yaml_file)


    def get_template(self):
        return self.naver_site["template"]

    def get_search(self):
        # print(self.naver_site["search"])
        return self.naver_site["search"]

    def get_menu(self):
        return self.naver_site["menu"]

    def get_review(self):
        return self.naver_site["review"]

    def get_blog_review(self):
        return self.naver_site["blog_review"]