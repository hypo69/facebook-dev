## \file ../src/advertisement/facebook/scenarios/post_message.py
## \file ../src/advertisement/facebook/scenarios/post_message.py
# -*- coding: utf-8 -*-
#! /usr/share/projects/hypotez/venv/scripts python
"""! Публикация сообщения """
...
from socket import timeout
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List
from selenium.webdriver.remote.webelement import WebElement
from src.settings import gs
from src.webdriver import Driver
from src.utils import j_loads_ns, pprint
from src.logger import logger

# Load locators from JSON file.
locator: SimpleNamespace = j_loads_ns(
    Path(gs.path.src, 'advertisement', 'facebook', 'locators', 'post_message.json')
)

def post_title(d: Driver, category: SimpleNamespace) -> bool:
    """! Sends the title and description of a campaign to the post message box.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        category (SimpleNamespace): The category containing the title and description to be sent.

    Returns:
        bool: `True` if the title and description were sent successfully, otherwise `None`.

    Examples:
        >>> driver = Driver(...)
        >>> category = SimpleNamespace(title="Campaign Title", description="Campaign Description")
        >>> post_title(driver, category)
        True
    """
    # Scroll backward in the page
    if not d.scroll(1, 1200, 'backward'):
        logger.error("Scroll failed during post title", exc_info=False)
        return

    # Open the 'add post' box
    if not d.execute_locator(locator = locator.open_add_post_box, timeout = 90):
        logger.error("Failed to open 'add post' box", exc_info=False)
        return

    # Construct the message with title and description
    message = f"{category.title}\n{category.description}"

    # Add the message to the post box
    if not d.execute_locator(locator.add_message, message):
        logger.error(f"Failed to add message to post box: {message=}", exc_info=False)
        return

    return True

def upload_media(d: Driver, products: List[SimpleNamespace], no_video: bool = False) -> bool:
    """! Uploads media files to the images section and updates captions.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        products (List[SimpleNamespace]): List of products containing media file paths.

    Returns:
        bool: `True` if media files were uploaded successfully, otherwise `None`.

    Raises:
        Exception: If there is an error during media upload or caption update.

    Examples:
        >>> driver = Driver(...)
        >>> products = [SimpleNamespace(image_local_saved_path='path/to/image.jpg', ...)]
        >>> upload_media(driver, products)
        True
    """
    # Step 1: Open the 'add media' form. It may already be open.
    if not d.execute_locator(locator.open_add_foto_video_form): 
        return
    d.wait(0.5)

    # Step 2: Ensure products is a list.
    products = products if isinstance(products, list) else [products]
    ret: bool = True

    # Iterate over products and upload media.
    for product in products:
        media_path = product.video_local_saved_path if hasattr(product, 'video_local_saved_path') and not no_video else product.image_local_saved_path
        try:
            # Upload the media file.
            if d.execute_locator(locator = locator.foto_video_input, message = media_path , timeout = 20):
                d.wait(1.5)
            else:
                logger.error(f"Ошибка загрузки изображения {media_path=}")
                return
        except Exception as ex:
            logger.error("Error in media upload", ex, exc_info=True)
            return

    # Step 3: Update captions for the uploaded media.
    if not d.execute_locator(locator.edit_uloaded_media_button):
        logger.error(f"Ошибка загрузки изображения {media_path=}")
        return
    uploaded_media_frame = d.execute_locator(locator.uploaded_media_frame)
    uploaded_media_frame = uploaded_media_frame[0] if isinstance(uploaded_media_frame, list) else uploaded_media_frame
    d.wait(0.3)

    textarea_list = d.execute_locator(locator.edit_image_properties_textarea)
    if not textarea_list:
        logger.error("Не нашлись поля ввода подписи к изображениям")
        return
    # Update image captions.
    if not update_images_captions(d, products, textarea_list):
        return

    return ret


def update_images_captions(d: Driver, products: List[SimpleNamespace], textarea_list: List[WebElement]) -> bool:
    """! Adds descriptions to uploaded media files.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        products (List[SimpleNamespace]): List of products with details to update.
        textarea_list (List[WebElement]): List of textareas where captions are added.

    Raises:
        Exception: If there's an error updating the media captions.
    """
    local_units = j_loads_ns(Path(gs.path.src / 'advertisement' / 'facebook' / 'scenarios' / 'translations.json'))

    def handle_product(product: SimpleNamespace, textarea_list: List[WebElement], i: int) -> bool:
        """! Handles the update of media captions for a single product.

        Args:
            product (SimpleNamespace): The product to update.
            textarea_list (List[WebElement]): List of textareas where captions are added.
            i (int): Index of the product in the list.
        """
        direction = getattr(local_units.LOCALE, product.language, "LTR")
        message = ""

        # Add product details to message.
        try:
            if direction == "LTR":
                if hasattr(product, 'product_title'):
                    message += f"{product.product_title}\n"
                if hasattr(product, 'original_price'):
                    message += f"{getattr(local_units.original_price, product.language)}: {product.original_price}\n"
                if hasattr(product, 'sale_price'):
                    message += f"{getattr(local_units.sale_price, product.language)}: {product.sale_price}\n"
                if hasattr(product, 'discount'):
                    message += f"{getattr(local_units.discount, product.language)}: {product.discount}\n"
                if hasattr(product, 'evaluate_rate'):
                    message += f"{getattr(local_units.evaluate_rate, product.language)}: {product.evaluate_rate}\n"
                if hasattr(product, 'promotion_link'):
                    message += f"{getattr(local_units.promotion_link, product.language)}: {product.promotion_link}\n"
                if hasattr(product, 'tags'):
                    message += f"{getattr(local_units.tags, product.language)}: {product.tags}\n"
                message += f"{getattr(local_units.COPYRIGHT, product.language)}"
                
            else:  # RTL direction
                if hasattr(product, 'product_title'):
                    message += f"\n{product.product_title}"
                if hasattr(product, 'original_price'):
                    message += f"\n{product.original_price} :{getattr(local_units.original_price, product.language)}"
                if hasattr(product, 'discount'):
                    message += f"\n{product.discount} :{getattr(local_units.discount, product.language)}"
                if hasattr(product, 'sale_price'):
                    message += f"\n{product.sale_price} :{getattr(local_units.sale_price, product.language)}"
                if hasattr(product, 'evaluate_rate'):
                    message += f"\n{product.evaluate_rate} :{getattr(local_units.evaluate_rate, product.language)}"
                if hasattr(product, 'promotion_link'):
                    message += f"\n{product.promotion_link} :{getattr(local_units.promotion_link, product.language)}"
                if hasattr(product, 'tags'):
                    message += f"\n{product.tags} :{getattr(local_units.tags, product.language)}"
                message += f"\n{getattr(local_units.COPYRIGHT, product.language)}"
                
        except Exception as ex:
            logger.error("Error in message generation", ex, exc_info=True)

        # Send message to textarea.
        try:
           textarea_list[i].send_keys(message) 
           return True
        except Exception as ex:
            logger.error("Error in sending keys to textarea", ex)

    # Process products and update their captions.
    for i, product in enumerate(products):
        if not handle_product(product, textarea_list, i):
            logger.debug(f"Неудача ввода в поле #{i}")

    return True


def promote_post(d: Driver, category: SimpleNamespace, products: List[SimpleNamespace], no_video: bool = False) -> bool:
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
    if not post_title(d, category): 
        return
    d.wait(0.5)

    if not upload_media(d, products, no_video): 
        return
    if not d.execute_locator(locator = locator.finish_editing_button): 
        return
    if not d.execute_locator(locator.publish, timeout = 20):
        print("Publishing...")
        return
    return True

from email import message
from socket import timeout
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List
from selenium.webdriver.remote.webelement import WebElement
from src.settings import gs
from src.webdriver import Driver
from src.utils import j_loads_ns, pprint
from src.logger import logger

# Load locators from JSON file.
locator: SimpleNamespace = j_loads_ns(
    Path(gs.path.src, 'advertisement', 'facebook', 'locators', 'post_message.json')
)

def post_title(d: Driver, category: SimpleNamespace) -> bool:
    """! Sends the title and description of a campaign to the post message box.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        category (SimpleNamespace): The category containing the title and description to be sent.

    Returns:
        bool: `True` if the title and description were sent successfully, otherwise `None`.

    Examples:
        >>> driver = Driver(...)
        >>> category = SimpleNamespace(title="Campaign Title", description="Campaign Description")
        >>> post_title(driver, category)
        True
    """
    # Scroll backward in the page
    if not d.scroll(1, 1200, 'backward'):
        logger.error("Scroll failed during post title", exc_info=False)
        return

    # Open the 'add post' box
    if not d.execute_locator(locator = locator.open_add_post_box, timeout = 120):
        logger.debug("Failed to open 'add post' box", exc_info=False)
        return

    # Construct the message with title and description
    message = f"{category.title}; {category.description};"

    # Add the message to the post box
    if not d.execute_locator(locator.add_message, message):
        logger.debug(f"Failed to add message to post box: {message=}", exc_info=False)
        return

    return True

def upload_media(d: Driver, products: List[SimpleNamespace], no_video: bool = False) -> bool:
    """! Uploads media files to the images section and updates captions.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        products (List[SimpleNamespace]): List of products containing media file paths.

    Returns:
        bool: `True` if media files were uploaded successfully, otherwise `None`.

    Raises:
        Exception: If there is an error during media upload or caption update.

    Examples:
        >>> driver = Driver(...)
        >>> products = [SimpleNamespace(image_local_saved_path='path/to/image.jpg', ...)]
        >>> upload_media(driver, products)
        True
    """
    # Step 1: Open the 'add media' form. It may already be open.
    if not d.execute_locator(locator.open_add_foto_video_form): 
        return
    d.wait(0.5)

    # Step 2: Ensure products is a list.
    products = products if isinstance(products, list) else [products]
    ret: bool = True

    # Iterate over products and upload media.
    for product in products:
        media_path = product.video_local_saved_path if hasattr(product, 'video_local_saved_path') and not no_video else product.image_local_saved_path
        try:
            # Upload the media file.
            if d.execute_locator(locator = locator.foto_video_input, message = media_path , timeout = 20):
                d.wait(1.5)
            else:
                logger.error(f"Ошибка загрузки изображения {media_path=}")
                return
        except Exception as ex:
            logger.error("Error in media upload", ex, exc_info=True)
            return

    # Step 3: Update captions for the uploaded media.
    if not d.execute_locator(locator.edit_uloaded_media_button):
        logger.error(f"Ошибка загрузки изображения {media_path=}")
        return
    uploaded_media_frame = d.execute_locator(locator.uploaded_media_frame)
    if not uploaded_media_frame:
        logger.debug(f"Не нашлись поля ввода подписей к изображениям")
        return

    uploaded_media_frame = uploaded_media_frame[0] if isinstance(uploaded_media_frame, list) else uploaded_media_frame
    d.wait(0.3)

    textarea_list = d.execute_locator(locator.edit_image_properties_textarea)
    if not textarea_list:
        logger.error("Не нашлись поля ввода подписи к изображениям")
        return
    # Update image captions.
    update_images_captions(d, products, textarea_list)

    return ret


def update_images_captions(d: Driver, products: List[SimpleNamespace], textarea_list: List[WebElement]) -> None:
    """! Adds descriptions to uploaded media files.

    Args:
        d (Driver): The driver instance used for interacting with the webpage.
        products (List[SimpleNamespace]): List of products with details to update.
        textarea_list (List[WebElement]): List of textareas where captions are added.

    Raises:
        Exception: If there's an error updating the media captions.
    """
    local_units = j_loads_ns(Path(gs.path.src / 'advertisement' / 'facebook' / 'scenarios' / 'translations.json'))

    def handle_product(product: SimpleNamespace, textarea_list: List[WebElement], i: int) -> None:
        """! Handles the update of media captions for a single product.

        Args:
            product (SimpleNamespace): The product to update.
            textarea_list (List[WebElement]): List of textareas where captions are added.
            i (int): Index of the product in the list.
        """
        direction = getattr(local_units.LOCALE, product.language, "LTR")
        message = ""

        # Add product details to message.
        try:
            if direction == "LTR":
                if hasattr(product, 'product_title'):
                    message += f"{product.product_title}\n"
                if hasattr(product, 'original_price'):
                    message += f"{getattr(local_units.original_price, product.language)}: {product.original_price}\n"
                if hasattr(product, 'sale_price'):
                    message += f"{getattr(local_units.sale_price, product.language)}: {product.sale_price}\n"
                if hasattr(product, 'discount'):
                    message += f"{getattr(local_units.discount, product.language)}: {product.discount}\n"
                if hasattr(product, 'evaluate_rate'):
                    message += f"{getattr(local_units.evaluate_rate, product.language)}: {product.evaluate_rate}\n"
                if hasattr(product, 'promotion_link'):
                    message += f"{getattr(local_units.promotion_link, product.language)}: {product.promotion_link}\n"
                if hasattr(product, 'tags'):
                    message += f"{getattr(local_units.tags, product.language)}: {product.tags}\n"
                message += f"{getattr(local_units.COPYRIGHT, product.language)}"
                
            else:  # RTL direction
                if hasattr(product, 'product_title'):
                    message += f"\n{product.product_title}"
                if hasattr(product, 'original_price'):
                    message += f"\n{product.original_price} :{getattr(local_units.original_price, product.language)}"
                if hasattr(product, 'discount'):
                    message += f"\n{product.discount} :{getattr(local_units.discount, product.language)}"
                if hasattr(product, 'sale_price'):
                    message += f"\n{product.sale_price} :{getattr(local_units.sale_price, product.language)}"
                if hasattr(product, 'evaluate_rate'):
                    message += f"\n{product.evaluate_rate} :{getattr(local_units.evaluate_rate, product.language)}"
                if hasattr(product, 'promotion_link'):
                    message += f"\n{product.promotion_link} :{getattr(local_units.promotion_link, product.language)}"
                if hasattr(product, 'tags'):
                    message += f"\n{product.tags} :{getattr(local_units.tags, product.language)}"
                message += f"\n{getattr(local_units.COPYRIGHT, product.language)}"
                
        except Exception as ex:
            logger.error("Error in message generation", ex, exc_info=True)

        # Send message to textarea.
        try:
           textarea_list[i].send_keys(message) 
           return True
        except Exception as ex:
            logger.error("Error in sending keys to textarea", ex)

    # Process products and update their captions.
    for i, product in enumerate(products):
        handle_product(product, textarea_list, i)


def post_message(d: Driver, category: SimpleNamespace, products: List[SimpleNamespace], no_video: bool = False) -> bool:
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
    if not post_title(d, category): 
        return
    d.wait(0.5)

    if not upload_media(d, products, no_video): 
        return
    if not d.execute_locator(locator = locator.finish_editing_button): 
        return
    if not d.execute_locator(locator.publish, timeout = 20): 
        return
    return True
