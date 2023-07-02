#!/bin/bash

export PATH=$PATH:/usr/local/bin:$HOME/.local/bin
DATE_WITH_TIME=`date "+%Y%m%dT%H%M%S"`
poetry run scrapy runspider scrape_main.py -O results/distinct_users.csv --logfile logs/scrape-main-${DATE_WITH_TIME}.log
