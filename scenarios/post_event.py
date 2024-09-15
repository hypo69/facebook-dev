## \file ../src/advertisement/facebook/scenarios/post_event.py
# -*- coding: utf-8 -*-
#! /usr/share/projects/hypotez/venv/scripts python
"""! Публикация календарного события v группах фейсбук"""
from socket import timeout
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List
from urllib.parse import urlencode
from selenium.webdriver.remote.webelement import WebElement

from src.settings import gs
from src.webdriver import Driver
from src.utils import j_loads_ns, pprint
from src.logger import logger

# Load locators from JSON file.
locator: SimpleNamespace = j_loads_ns(
    Path(gs.path.src, 'advertisement', 'facebook', 'locators', 'post_event.json')
)

def post_title(d: Driver, event: SimpleNamespace) -> bool:
    """! Sends the title of event.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        event (SimpleNamespace): The event containing the title, data of event and description to be sent.

    Returns:
        bool: `True` if the title and description were sent successfully, otherwise `None`.

    Examples:
        >>> driver = Driver(...)
        >>> event = SimpleNamespace(title="Campaign Title", description="Event Description")
        >>> post_title(driver, event)
        True
    """

    # Send title for event
    if not d.execute_locator(locator = locator.event_title, message = event.title):
        logger.error("Failed to send event title", exc_info=False)
        return
    return True

def post_date(d: Driver, event: SimpleNamespace) -> bool:
    """! Sends the title of event.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        event (SimpleNamespace): The event containing the title, data of event and description to be sent.

    Returns:
        bool: `True` if the title and description were sent successfully, otherwise `None`.

    Examples:
        >>> driver = Driver(...)
        >>> event = SimpleNamespace(title="Campaign Title", description="Event Description")
        >>> post_title(driver, event)
        True
    """

    # Send start_date for event
    date, time = event.start.split() 
    if not d.execute_locator(locator = locator.start_date, message = date):
        logger.error("Failed to send event date", exc_info=False)
        return
    return True

def post_time(d: Driver, event: SimpleNamespace) -> bool:
    """! Sends the title of event.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        event (SimpleNamespace): The event containing the title, data of event and description to be sent.

    Returns:
        bool: `True` if the title and description were sent successfully, otherwise `None`.

    Examples:
        >>> driver = Driver(...)
        >>> event = SimpleNamespace(title="Campaign Title", description="Event Description")
        >>> post_title(driver, event)
        True
    """
    ...
    # Send start_time for event
    date, time = event.start.split() 
    if not d.execute_locator(locator = locator.start_time, message = time):
        logger.error("Failed to send event time", exc_info=False)
        return
    return True

def post_description(d: Driver, event: SimpleNamespace) -> bool:
    """! Sends the title of event.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        event (SimpleNamespace): The event containing the title, data of event and description to be sent.

    Returns:
        bool: `True` if the title and description were sent successfully, otherwise `None`.

    Examples:
        >>> driver = Driver(...)
        >>> event = SimpleNamespace(title="Campaign Title", description="Event Description")
        >>> post_title(driver, event)
        True
    """
    ...
    # Send title for event
    d.scroll(1,300,'down')
    if not d.execute_locator(locator = locator.event_description, message = f"{event.description}\n{event.promotional_link}"):
        logger.error("Failed to send event description", exc_info=False)
        return
    return True


def post_event(d: Driver, event: SimpleNamespace) -> bool:
    """! Manages the process of promoting a post with a title, description, and media files.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        category (SimpleNamespace): The category details used for the post title and description.
        products (List[SimpleNamespace]): List of products containing media and details to be posted.

    Examples:
        >>> driver = Driver(...)
        >>> category = SimpleNamespace(title="Campaign Title", description="Campaign Description")
        >>> products = [SimpleNamespace(image_local_saved_path='path/to/image.jpg', ...)]
        >>> promote_post(driver, category, products)
    """
    if not post_title(d, event): 
        return
    # if not post_date(d, event): 
    #     return
    # if not post_time(d, event): 
    #     return
    if not post_description(d, event): 
        return
    if not d.execute_locator(locator = locator.event_send): 
        return
    time.sleep(30)
    #input()
    return True


