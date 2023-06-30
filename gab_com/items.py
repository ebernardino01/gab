# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class UserItem(Item):
    user_url = Field()


class UserDetailItem(Item):
    date_joined = Field()
    user_name = Field()
    user_image = Field()
    cover_photo = Field()
    about = Field()
    gab_count = Field()
    follower_count = Field()
    following_count = Field()
    posts = Field()


class UserPostItem(Item):
    id = Field()
    datetime = Field()
    text = Field()
    media_image = Field()
    media_video = Field()
    engagement = Field()
