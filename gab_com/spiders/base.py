from scrapy import Request, Spider
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BaseSpider(Spider):
    name = "base"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://www.gab.com"

    # Use an initial website to start scrapy request
    def start_requests(self):
        yield Request(url=self.base_url, callback=self.parse)

    # Setup the driver
    def setup_chromedriver(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument(f"--user-agent={get_project_settings().get('USER_AGENT')}")
        options.add_argument("--aggressive-cache-discard")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
