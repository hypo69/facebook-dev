﻿## \file ../src/advertisement/facebook/facebook.py
## \file ../src/advertisement/facebook/facebook.py
# -*- coding: utf-8 -*-
#! /usr/share/projects/hypotez/venv/scripts python
"""!  Модуль рекламы на фейсбук

Испонемые сценарии:
	- login: логин на фейсбук
	- post_message: отправка текствого сообщения в форму 
	- upload_media: Загрузка файла или списка файлов
"""

import os, sys
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List
...
from src.settings import gs
from src.webdriver import Driver
from src.utils import j_loads, j_dumps, pprint
from src.logger import logger
from .scenarios.login import login
from .scenarios import  switch_account, promote_post,  post_title, upload_media, update_images_captions


class Facebook():
	"""!  Класс общается с фейбуком через вебдрайвер """
	driver = None
	start_page:str = r'https://www.facebook.com/hypotez.promocodes'
																		
	def __init__(self, driver:Driver, *args, **kwards):
		"""! Я могу передать уже запущенный инстанс драйвера. Например, из алиэкспресс
		@todo:
			- Добавить проверку на какой странице открылся фейсбук. Если открылась страница логина - выполнитл сценарий логина
		"""
		...
		self.driver = driver	
		self.driver.get_url (self.start_page)
		#switch_account(self.driver) # <- переключение профиля, если не на своей странице

	def login(self) -> bool:
		return login(self)

	def promote_post(self, message:str) -> bool:
		"""! Функция отправляет текст в форму сообщения 
		@param message: сообщение текстом. Знаки `;` будут заменеы на `SHIFT+ENTER`
		@returns `True`, если успешно, иначе `False`
		"""
		...
		return  promote_post(self.driver, message)
	
	def promote_event(self,event:SimpleNamespace):
		""""""
		...
	
	

		
		
		
	    

		