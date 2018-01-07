#!/usr/bin/env python3
"""
Web Scraping from Box Office Mojo (http://www.boxofficemojo.com)
"""

import csv
import os
import re
import sys

from progressbar import ProgressBar

from utils import request

def index(mode=None, path='.'):
    """
    Scrape index of people from Box Office Mojo
    """
    options = {
        'actors': 'Actor',
        'directors': 'Director',
        'producers': 'Producer',
        'screenwriters': 'Writer',
        'cinematographers': 'Cinematographer',
        'composers': 'Composer'
    }
    if mode not in options.keys():
        raise ValueError
    print('Scraping index of movie {} from Box Office Mojo...'.format(mode))
    sys.stdout.flush()
    
    n = 3 if mode == 'actors' else 2 if mode == 'directors' else 1
    URL = (
        'http://www.boxofficemojo.com'
        + '/people'
        + '/'
        + '?view={}'.format(options[mode])
        + (
              '&pagenum={}'
            + '&sort=person'
            + '&order=ASC'
            if n != 1 else ''
        )
        + '&p=.htm'
    )
    path += '/features'
    if not os.path.exists(path):
        os.mkdir(path)
    with open('{}/{}.csv'.format(path, mode), 'w', newline='') as file:
        writer = csv.writer(file)
        header = [
            mode.rstrip('s'),
            'gross_total',
            'movie_count',
            'gross_average'
        ]
        writer.writerow(header)
        bar = ProgressBar()
        for i in bar(range(1, n + 1)):
            try:
                soup = request(URL.format(i))
            except TimeoutError:
                return 'TimeoutError'
            index = soup.find_all('table')[-1].find_all('tr')[1:]
            for row in index:
                row = [e.get_text() for e in row.find_all('td')[:4]]
                for j in [1, 3]:
                    e = re.sub('[$,]', '', row[j])
                    if 'k' in e:
                        e = 1e3 * float(e.rstrip('k'))
                    else:
                        e = 1e6 * float(e)
                    row[j] = int(e)
                writer.writerow(row)
    
    print('— PROCESS COMPLETED —', '\n')