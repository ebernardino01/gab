# Social Media Data Scraping
This project extracts user and user details from gab.com using Scrapy and Selenium. <br/>
Scraped output are exported as a `csv` file. <br/>

## Setup Environment
* Install `poetry` https://python-poetry.org/docs/
* Install the dependencies by running the command `poetry install`

## Running Scripts
* Run the following command to scrape a list of 100 user URLs: <br/>
`sh scrape_main.sh` <br/>
* Run the following command to scrape details of a specified user: <br/>
`sh scrape_user.sh a`
