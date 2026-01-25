#######################################################################
# Project: Data Retrieval Module
# File: date_utils.py
# Description: Util functions for date operations
# Author: AbigailWilliams1692
# Created: 2026-01-24
# Updated: 2026-01-24
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import datetime
from typing import List, Tuple


#######################################################################
# Util Functions
#######################################################################
def populate_dates_in_between(
    start_date: datetime.date, 
    end_date: datetime.date, 
    interval: int = 1
) -> List[datetime.date]:
    """
    Populate a list of dates between start_date and end_date (inclusive).
    
    :param start_date: The start date.
    :param end_date: The end date.
    :param interval: The interval between dates in days.
    :return: List of dates between start_date and end_date.
    """
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")
    delta = end_date - start_date
    return [start_date + datetime.timedelta(days=i) for i in range(0, delta.days + 1, interval)]


def populate_start_and_end_dates(
    start_date: datetime.date, 
    end_date: datetime.date, 
    interval: int = 1
) -> List[Tuple[datetime.date, datetime.date]]:
    """
    Populate a list of dates between start_date and end_date (inclusive).
    
    :param start_date: The start date.
    :param end_date: The end date.
    :param interval: The interval between dates in days.
    :return: List of start date and end date tuples.
    """
    date_list = populate_dates_in_between(start_date=start_date, end_date=end_date, interval=interval)
    return [(date_list[i], date_list[i+1]) for i in range(0, len(date_list)-1)]
