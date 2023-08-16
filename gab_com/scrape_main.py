from logging import ERROR, getLogger

from common import run_spider
from spiders.main_spider import MainSpider

logger = getLogger(__name__)
logger.setLevel(ERROR)


class GabMainSpider(MainSpider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [self.base_url]


if __name__ == "__main__":
    run_spider(GabMainSpider)
