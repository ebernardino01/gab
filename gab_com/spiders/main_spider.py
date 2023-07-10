import time
from logging import ERROR

from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from selenium.webdriver.remote.remote_connection import LOGGER

from .base import BaseSpider
from gab_com.items import UserItem


LOGGER.setLevel(ERROR)


class MainSpider(BaseSpider):
    name = 'main_spider'

    def parse(self, response):
        driver = self.setup_chromedriver()
        driver.implicitly_wait(get_project_settings().get('GAB_DRIVER_IMPLICIT_WAIT'))
        driver.maximize_window()

        # Load the page
        driver.delete_all_cookies()
        driver.get(self.base_url)

        # Wait first to load
        time.sleep(5)

        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        pages = []
        while True:
            # Save the current page
            pages.append(driver.page_source)

            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(get_project_settings().get('GAB_SCROLL_PAUSE_TIME'))

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract the list of users
        users = []
        for page in pages:
            selector = Selector(text=page)
            row_post = selector.xpath('//div[@class="_81_1w" and @tabindex="-1"]')
            for row in row_post:
                user = row.xpath('.//span[contains(@class, "_3_54N")]/text()').get()
                users.append(user.replace('@', ''))

        # Remove duplicates from the list
        distinct_users = [*set(users)]
        driver.quit()

        # Harvest up to 100 users at maximum
        users_limit = get_project_settings().get('GAB_USER_LIMIT')
        if len(distinct_users) < users_limit:
            users_limit = len(distinct_users)

        # Iterate through each user within the specified limit
        for user in distinct_users[:users_limit]:
            user_item = UserItem()
            user_item['user_url'] = f'{self.base_url}/{user}'
            yield user_item
