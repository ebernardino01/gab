import time
from datetime import datetime
from logging import ERROR

from html2text import html2text
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from selenium.webdriver.remote.remote_connection import LOGGER

from gab_com.items import UserDetailItem, UserPostItem
from gab_com.settings import (
    GAB_DRIVER_IMPLICIT_WAIT,
    GAB_DRIVER_LOAD_WAIT,
    GAB_SCROLL_POST_PAUSE_TIME,
    GAB_USER_POST_LIMIT,
)

from .base import BaseSpider

LOGGER.setLevel(ERROR)


class UserSpider(BaseSpider):
    name = "user_spider"

    def parse(self, response):
        driver = self.setup_chromedriver()
        driver.implicitly_wait(GAB_DRIVER_IMPLICIT_WAIT)
        driver.maximize_window()

        for url in self.start_urls:
            # Load the page
            driver.delete_all_cookies()
            driver.get(url)

            # Wait first to load
            time.sleep(GAB_DRIVER_LOAD_WAIT)
            selector = Selector(text=driver.page_source)

            # Get the following user information
            # Date joined
            user_detail_item = UserDetailItem()
            user_detail_item["date_joined"] = selector.xpath(
                '//div[@class="_UuSG _3dGg1 _2mtbj"]/span/text()'
            ).get()

            # User name
            user_detail_item["user_name"] = selector.xpath(
                '//div[@class="_UuSG Naf1t"]/span[2]/text()'
            ).get()

            # User Image
            user_detail_item["user_image"] = selector.xpath(
                '//div[@class="_UuSG _3mBt0 _1FVXP _1lNuM _2I3eh"]/img/@src'
            ).get()

            # Cover photo
            user_detail_item["cover_photo"] = selector.xpath(
                '//div[@class="_UuSG _2Ap7s w77Za _3F-hn jpgPp _2z1u_"]/img/@src'
            ).get()

            # About (need to convert HTML string to plain text)
            about = selector.xpath('//div[@class="_9utbn"]').get()
            about_text = html2text(about) if about else None
            user_detail_item["about"] = None
            if about_text:
                user_detail_item["about"] = about_text.replace("\n", "")

            # Number of Gabs
            rows_count = selector.xpath('//div[@class="_UuSG _3dGg1"]')
            gab_count_text = rows_count.xpath(".//a[1]/@title").get()
            user_detail_item["gab_count"] = (
                gab_count_text.split(" ")[0] if gab_count_text else None
            )

            # Number of Followers
            follower_count_text = rows_count.xpath(".//a[2]/@title").get()
            user_detail_item["follower_count"] = (
                follower_count_text.split(" ")[0] if follower_count_text else None
            )

            # Number of Following
            following_count_text = rows_count.xpath(".//a[3]/@title").get()
            user_detail_item["following_count"] = (
                following_count_text.split(" ")[0] if following_count_text else None
            )

            # Check if there is available user posts to scrape
            row_no_post = selector.xpath(
                '//span[@class="_2FoTG _UuSG _3_54N _2ZzNB _3hcKE L4pn5 _1XpDY"]'
            )
            if not row_no_post:
                # ● Last 50 posts(including media in case it’s exists)
                # ● Average engagement of the posts
                # Limit to 30 pages, should be enough to fetch the recent 50 posts
                pages = []
                for _ in range(1, 31):
                    # Check if the current page is the same as the last captured page
                    current_page_source = driver.page_source
                    if pages and pages[-1] == current_page_source:
                        break

                    # Save the current page
                    pages.append(current_page_source)

                    # Scroll down to bottom
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )

                    # Wait to load page
                    time.sleep(GAB_SCROLL_POST_PAUSE_TIME)

                # Loop through each saved page to scrape the posts
                user_posts = []
                for page in pages:
                    selector = Selector(text=page)
                    row_post = selector.xpath(
                        '//div[@class="_81_1w" and @tabindex="-1"]'
                    )
                    for row in row_post:
                        # Exclude reposts
                        row_repost = row.xpath(
                            './/div[contains(@aria-label, "reposted")]'
                        )
                        if row_repost:
                            continue

                        # Post unique id
                        post = UserPostItem()
                        post["id"] = row.xpath(
                            './/div[@class="_UuSG _2z1u_"]/div/@data-id'
                        ).get()

                        # Post date and time
                        datetime_value = row.xpath(".//time/@datetime").get()
                        datetime_value_string = datetime_value if datetime_value else ""
                        post["datetime"] = datetime.strptime(
                            datetime_value_string, "%Y-%m-%dT%H:%M:%S.%fZ"
                        )

                        # Post text content (need to convert HTML string to plain text)
                        row_text = row.xpath(
                            './/div[contains(@class, "_1FwZr") and contains(@class, "_81_1w")]'
                        ).get()
                        post_text = html2text(row_text) if row_text else None
                        post["text"] = None
                        if post_text:
                            post["text"] = post_text.replace("\n", "")

                        # Post media (image and video if present)
                        media_element = row.xpath('.//div[@data-container="true"]')
                        post["media_image"] = media_element.xpath(".//img/@src").get()
                        post["media_video"] = media_element.xpath(
                            ".//div/div/@src"
                        ).get()

                        # Post engagements (reactions, replies, reposts, quotes)
                        engagement_row = row.xpath(
                            './/div[@class="_UuSG _3dGg1 _2VJFi SslQJ _2pVfg"]'
                        )
                        engagements = engagement_row.xpath(
                            './/span[contains(@class, "RiX17")]'
                        )
                        engagement_list = []
                        for index, engagement in enumerate(engagements):
                            # Need to convert HTML string to plain text
                            engagement_text = engagement.get()
                            post_engagement = (
                                html2text(engagement_text) if engagement_text else None
                            )
                            if index == 0:
                                if post_engagement:
                                    post_engagement = f"{post_engagement} reactions"
                                else:
                                    post_engagement = ""
                            engagement_list.append(
                                post_engagement.replace("\n", "")
                                if post_engagement
                                else ""
                            )

                        post["engagement"] = engagement_list
                        user_posts.append(post)

                # Remove duplicates from the list
                distinct_user_posts = [
                    i for n, i in enumerate(user_posts) if i not in user_posts[n + 1 :]
                ]

                # Sort distinct list by datetime (recent posts)
                distinct_user_posts_sorted = sorted(
                    distinct_user_posts, key=lambda x: x["datetime"], reverse=True
                )

                # Harvest up to 50 user posts at maximum
                user_posts_limit = get_project_settings().get("GAB_USER_POST_LIMIT")
                if len(distinct_user_posts_sorted) < GAB_USER_POST_LIMIT:
                    user_posts_limit = len(distinct_user_posts_sorted)

                # Loop through list of posts and add to detail item main structure
                user_detail_item["posts"] = [
                    user_post
                    for user_post in distinct_user_posts_sorted[:user_posts_limit]
                ]

            yield user_detail_item

        driver.quit()
