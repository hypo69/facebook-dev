## \file ../src/advertisement/facebook/promoter.py
## \file ../src/advertisement/facebook/promoter.py
# -*- coding: utf-8 -*-
# /path/to/interpreter/python
"""
This module handles the promotion of messages and events in Facebook groups.
It processes campaigns and events, posting them to Facebook groups while avoiding duplicate promotions.
"""
...
import time
from datetime import datetime, timedelta
from pathlib import Path
import re
from urllib.parse import urlencode
from types import SimpleNamespace

from src import gs
from src.webdriver import Driver, Chrome
from src.suppliers.aliexpress.campaign import AliCampaignEditor
from src.advertisement.facebook.scenarios import post_message, post_event
from src.utils import get_filenames, get_directory_names
from src.utils import j_loads_ns, j_dumps
from src.utils.cursor_spinner import spinning_cursor
from src.logger import logger

def get_event_url(group_url: str) -> str:
    """
    Returns the modified URL for creating an event on Facebook, replacing `group_id` with the value from the input URL.

    Args:
        group_url (str): Facebook group URL containing `group_id`.
        event_id (str): Event identifier.

    Returns:
        str: Modified URL for creating the event.
    """
    group_id = group_url.rstrip('/').split('/')[-1]
    base_url = "https://www.facebook.com/events/create/"
    params = {
        "acontext": '{"event_action_history":[{"surface":"group"},{"mechanism":"upcoming_events_for_group","surface":"group"}],"ref_notif_type":null}',
        "dialog_entry_point": "group_events_tab",
        "group_id": group_id
    }

    query_string = urlencode(params)
    return f"{base_url}?{query_string}"

class FacebookPromoter:
    """ Class for promoting AliExpress products and events in Facebook groups.
    
    This class automates the posting of promotions to Facebook groups using a WebDriver instance,
    ensuring that categories and events are promoted while avoiding duplicates.
    """
    d:Driver = None
    group_file_paths: str | Path = None
    no_video:bool = False
    def __init__(self, d: Driver, group_file_paths: list[str | Path] | str | Path, no_video: bool = False):
        """ Initializes the promoter for Facebook groups.

        Args:
            d (Driver): WebDriver instance for browser automation.
            group_file_paths (list[str | Path] | str | Path): List of file paths containing group data.
            no_video (bool, optional): Flag to disable videos in posts. Defaults to False.
        """
        self.d = d
        self.group_file_paths = group_file_paths if group_file_paths else get_filenames(gs.path.data / 'facebook' / 'groups')
        self.no_video = no_video
        self.spinner = spinning_cursor()

    def parse_interval(self, interval: str) -> timedelta:
        """ Converts a string interval to a timedelta object.

        Args:
            interval (str): Interval in string format (e.g., '1H', '6M').

        Returns:
            timedelta: Corresponding timedelta object.

        Raises:
            ValueError: If the interval format is invalid.

        Example:
            >>> result = parse_interval('1H')
            >>> print(result)
            1:00:00
        """
        match = re.match(r"(\d+)([HM])", interval)
        if not match:
            raise ValueError(f"Invalid interval format: {interval}")
        value, unit = match.groups()
        return timedelta(hours=int(value)) if unit == "H" else timedelta(minutes=int(value))

    def promote(self, group: SimpleNamespace, item: SimpleNamespace, is_event: bool = False) -> bool:
        """ Promotes a category or event in a Facebook group.

        Args:
            group (SimpleNamespace): Group object with promotion data.
            item (SimpleNamespace): The category or event to be promoted.
            is_event (bool, optional): Flag indicating if the item is an event. Defaults to False.

        Returns:
            bool: True if the item was successfully promoted, otherwise False.

        Example:
            >>> group = SimpleNamespace(promoted_events=[], promoted_categories={})
            >>> item = SimpleNamespace(event_name="Sale Event")
            >>> result = promote(group, item, is_event=True)
            >>> print(result)
            True
        """
        ...


        item_name = item.event_name if is_event else item.category_name

        if item_name in (group.promoted_events if is_event else group.promoted_categories):
            logger.debug(f"# Item already promoted", None, False)
            return False  # Item already promoted


        self.d.get_url(get_event_url(group.group_url) if is_event else group.group_url)
        if is_event:

            ev = getattr(item.language, group.language )
            ev.start = item.start  # <- Дата Начало мероприятия
            ev.end = item.end      # <- Дата окончания мероприятия
            ev.promotional_link = item.promotional_link
            if not post_event(d=self.d, event=ev ):
                logger.debug(f"Error while posting {'event' if is_event else 'category'} {item_name}", None, False)
                return False
        else:
            if not post_message(d=self.d,  category=item if not is_event else None, no_video=self.no_video):
                logger.debug(f"Error while posting {'event' if is_event else 'category'} {item_name}", None, False)
                return False


        timestamp = datetime.now().strftime("%d/%m/%y %H:%M")
        if is_event:
            group.promoted_events.append(item_name)
        else:
            group.promoted_categories.append(item_name)
            #group.promoted_categories[item_name] = timestamp

        group.last_promo_sended = timestamp
        input("Next")
        return True

    def process_groups(self, campaign_name: str = None, events: list[SimpleNamespace] = None, is_event: bool = False, group_file_paths: list[str] = None):
        """ Processes all groups for the current campaign or event promotion.

        Args:
            group_file_paths (list[str]): List of file paths containing group data.
            campaign_name (str): The name of the campaign being promoted.
            is_event (bool, optional): Flag indicating if processing is for events. Defaults to False.
            events (list[SimpleNamespace], optional): List of events to promote if promoting events.

        Example:
            >>> promoter = FacebookPromoter(d=Driver(Chrome), group_file_paths=["group1.json"], no_video=True)
            >>> promoter.process_groups(group_file_paths=["group1.json"], campaign_name="Winter Campaign")
        """
        if not campaign_name and not events:
            logger.debug(f"Nothing to promote!")
            return

        for group_file in group_file_paths:
            path_to_group_file: Path = gs.path.data / 'facebook' / 'groups' / group_file
            groups_ns: dict = j_loads_ns(path_to_group_file)
            #logger.info(f"Loaded groups from {group_file}")

            for group_url, group in vars(groups_ns).items():
                group.group_url = group_url
                if not is_event and not self.check_interval(group):
                    continue


                
                if not is_event:
                    # Only create AliCampaignEditor for campaigns, not for events
                    ce = AliCampaignEditor(campaign_name=campaign_name, language=group.language, currency=group.currency)
                    items_to_promote = vars(ce.campaign.category).values()
                else:
                    items_to_promote = events

                for item in items_to_promote:
                    #logger.info(f"Start promoting {'event' if is_event else 'category'}: {item.event_name if is_event else item.category_name} for {group_url}")
                    item.products = ce.get_category_products(item.category_name) if not is_event else None                    
                    if not self.promote(group=group, item=item,  is_event=is_event):
                        logger.debug(f"Failed to promote {'event' if is_event else 'category'}: {item.event_name if is_event else item.category_name}", None, False)

                j_dumps(groups_ns, path_to_group_file)

    def check_interval(self, group: SimpleNamespace) -> bool:
        """ Checks if the required interval has passed for the next promotion.

        Args:
            group (SimpleNamespace): Group to check.

        Returns:
            bool: True if the interval has passed, otherwise False.

        Raises:
            ValueError: If the interval format is invalid.

        Example:
            >>> group = SimpleNamespace(interval="1H", last_promo_sended="01/01/23 10:00")
            >>> result = check_interval(group)
            >>> print(result)
            True
        """
        try:
            interval_timedelta = self.parse_interval(group.interval) if hasattr(group, 'interval') else timedelta()
            last_promo_time = datetime.strptime(group.last_promo_sended, "%d/%m/%y %H:%M") if hasattr(group, 'last_promo_sended') else None
            return not last_promo_time or datetime.now() - last_promo_time >= interval_timedelta
        except ValueError as e:
            logger.error(f"Error parsing interval for group {group.group_url}: {e}")
            return False

    def run_campaigns(self, campaigns: list[str], group_file_paths: list[str] = None):
        """ Runs the campaign promotion cycle for all groups and categories sequentially.

        Args:
            campaigns (list[str]): List of campaign names to promote.
            group_file_paths (list[str]): List of file paths containing group data.

        Example:
            >>> promoter.run_campaigns(campaigns=["Campaign1", "Campaign2"], group_file_paths=["group1.json", "group2.json"])
        """
        for campaign_name in campaigns:
            #logger.info(f"Processing campaign: {campaign_name}")
            self.process_groups(group_file_paths = group_file_paths if group_file_paths else self.group_file_paths, campaign_name = campaign_name)

    def run_events(self, events: list[SimpleNamespace], group_file_paths: list[str]):
        """ Runs event promotion in all groups sequentially.

        Args:
            events (list[SimpleNamespace]): List of events to promote.
            group_file_paths (list[str]): List of file paths containing group data.

        Example:
            >>> event = SimpleNamespace(event_name="Special Event")
            >>> promoter.run_events(events=[event], group_file_paths=["group1.json", "group2.json"])
        """
        self.process_groups(group_file_paths=group_file_paths, campaign_name="", is_event=True, events=events)

    def stop(self):
        """ Stops the promotion process by quitting the WebDriver instance.

        Example:
            >>> promoter.stop()
        """
        self.d.quit()

# Example usage:
if __name__ == "__main__":
    group_files = ["ru_usd.json", "usa.json", "ger_en_eur.json", "he_il.json", "ru_il.json"]
    promoter = FacebookPromoter(d=Driver(Chrome), group_file_paths=group_files, no_video=True)

    try:
        promoter.run_campaigns(campaigns=["campaign1", "campaign2"], group_file_paths=group_files)
        # promoter.run_events(events=[event1, event2], group_file_paths=group_files)
    except KeyboardInterrupt:
        print("Campaign promotion interrupted.")
