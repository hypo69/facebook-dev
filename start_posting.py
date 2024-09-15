## \file ../src/advertisement/facebook/start_posting.py
# -*- coding: utf-8 -*-
#! /usr/share/projects/hypotez/venv/scripts python
"""!Отправка рекламных объявлений в группы фейсбук """

import header 
from src.webdriver import Driver, Chrome
from src.advertisement.facebook import FacebookPromoter
from src.logger import logger

d = Driver(Chrome)
d.get_url(r"https://facebook.com")

filenames:list[str] = [
            "ru_usd.json",
            "usa.json",
            "ger_en_eur.json",
            "he_il.json",
            "ru_il.json",
             ]
excluded_filenames:list[str] = ["my_managed_groups.json",]

promoter:FacebookPromoter = FacebookPromoter(d, group_file_paths=filenames, no_video=True)

try:
    promoter.run_campaigns(filenames)
except KeyboardInterrupt:
    logger.info("Campaign promotion interrupted.")