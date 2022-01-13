import os.path

import yaml
from config import Config as cfg

yaml.warnings({'YAMLLoadWarning': False})

class GoogleConfig:

    def __init__(self):

        for filename in os.listdir(cfg.template_path):
            abs_file_path = os.path.abspath("template//google-site.yaml")
            with open(abs_file_path, 'r') as yaml_file:
                self.google_site = yaml.load(yaml_file)


    def get_template(self):
        return self.google_site["template"]

    def get_search(self):
        return self.google_site["search"]

    def get_menu(self):
        return self.google_site["menu"]

    def get_review(self):
        return self.google_site["review"]

    def get_blog_review(self):
        return self.google_site["blog_review"]