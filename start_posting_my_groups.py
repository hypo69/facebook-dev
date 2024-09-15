## \file ../src/advertisement/facebook/start_posting_my_groups.py
# -*- coding: utf-8 -*-
#! /usr/share/projects/hypotez/venv/scripts python
"""!Отправка рекламных объявлений в группы фейсбук """

import header 
from src.webdriver import Driver, Chrome
from src.advertisement.facebook import FacebookCampaignPromoter
from src.logger import logger

d = Driver(Chrome)
d.get_url(r"https://facebook.com")

filenames = ["my_managed_groups.json",]

promoter = FacebookCampaignPromoter(d, group_file_paths = filenames, no_video = False)

try:
    promoter.run_campaigns()
except KeyboardInterrupt:
    logger.info("Campaign promotion interrupted.")