import csv

from logging import getLogger, ERROR
from common import run_spider
from spiders.user_spider import UserSpider


logger = getLogger(__name__)
logger.setLevel(ERROR)


class GabUserSpider(UserSpider):
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [f'{self.base_url}/{user}']


if __name__ == '__main__':
    run_spider(GabUserSpider)
