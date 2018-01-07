#!/usr/bin/env python3
"""
Utilities for Web Scraping
"""

import requests

from bs4 import BeautifulSoup

def request(URL):
    """
    Request and parse a Response object into a BeautifulSoup object
    """
    try:
        r = requests.get(URL)
    except:
        raise TimeoutError
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='UTF-8')
    return soup
