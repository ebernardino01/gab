#!/bin/bash

export PATH=$PATH:/usr/local/bin:$HOME/.local/bin
DATE_WITH_TIME=`date "+%Y%m%dT%H%M%S"`
poetry run scrapy runspider scrape_user.py -a user=$1 -O results/$1-details-${DATE_WITH_TIME}.csv --logfile logs/scrape-user-list-${DATE_WITH_TIME}.log
