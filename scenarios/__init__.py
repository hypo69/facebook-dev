""" Сценарии фейсбука """
## \file ../src/advertisement/facebook/scenarios/__init__.py
# -*- coding: utf-8 -*-
# /path/to/interpreter/python

from packaging.version import Version
from .version import __version__,  __doc__, __details__

from .login import login
from .post_message  import *
from .switch_account import switch_account
from .post_message import (post_title,   # <- заголовок
                           upload_media, # <- изображения 
                           update_images_captions, # <- подписи к изображениям 
                           #send  # <- отправка сообщения,
                           post_message
                           )

from .post_event import (post_title,
                         post_description,
                         post_date,
                         post_time,
                         #send,
                         post_event
                         )