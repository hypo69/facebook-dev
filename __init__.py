﻿## \file ../src/advertisement/facebook/__init__.py
# -*- coding: utf-8 -*-

from packaging.version import Version
from .version import __version__, __doc__, __details__

from .facebook import Facebook
from .promoter import FacebookPromoter, get_event_url