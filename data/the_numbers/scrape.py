#!/usr/bin/env python3
"""
Web Scraping from The Numbers (https://www.the-numbers.com)
"""

import csv
import os
import re
import sys

from datetime import datetime
from progressbar import ProgressBar

from utils import request

def charts(mode=None, path='.'):
    """
    Scrape domestic theatrical box office charts
    """
    options = {
        'daily': '',
        'weekend': '',
        'weekly': '',
    }
    if mode not in options.keys():
        raise ValueError
    print('Scraping domestic theatrical {} box office charts from The Numbers...'.format(mode))
    sys.stdout.flush()
    
    # Calendar of Years
    print('\n', 'Part 1: Scraping calendar of years...')
    sys.stdout.flush()
    URL = (
        'https://www.the-numbers.com'
        + '/box-office'
    )
    bar = ProgressBar(max_value=1)
    bar.update(0)
    try:
        soup = request(URL)
    except TimeoutError:
        return 'TimeoutError'    
    calendar = [e.get_text() for e in soup.find_all('option')[1:]]
    bar.update(1)
    
    # Index of Charts by Year
    print('\n', 'Part 2: Scraping index of {} charts by year...'.format(mode))
    sys.stdout.flush()
    URL += '/{}'
    bar, index = ProgressBar(), []
    for year in bar(calendar):
        try:
            soup = request(URL.format(year))
        except TimeoutError:
            return 'TimeoutError'
        index.extend([a.get('href') for a in soup.table.find_all('a', href=re.compile(mode))])
    index = [a.lstrip('/box-office-chart/{}/'.format(mode)) for a in index]
    
    # Charts
    print('\n', 'Part 3: Scraping {} charts...'.format(mode))
    sys.stdout.flush()
    URL = (
        'https://www.the-numbers.com'
        + '/box-office-chart'
        + '/{}'.format(mode)
        + '/{}'
    )
    path += '/charts'
    if not os.path.exists(path):
        os.mkdir(path)
    with open('{}/{}.csv'.format(path, mode), 'w', newline='') as file:
        writer = csv.writer(file)
        header = [
            ('day' if mode == 'daily' else 'weekend' if mode == 'weekend' else 'week'),
            'rank_t+0',
            'rank_t-1',
            'movie_ID',
            'distributor_ID',
            'gross',
            'change',
            'theater_count',
            'gross_average',
            'gross_total',
            '{}_in_release'.format('day' if mode == 'daily' else 'week')
        ]
        writer.writerow(header)
        bar, log = ProgressBar(), []
        for a in bar(index):
            try:
                soup = request(URL.format(a))
            except TimeoutError:
                log.append((index.index(a), a))
                continue
            chart = soup.find_all('table')[1].find_all('tr')[1:]
            for i in range(len(chart)):
                row = [e.get_text() for e in chart[i].find_all('td')]
                row.insert(0, a.replace('/', '-'))
                try:
                    row[3] = chart[i].find_all('td')[2].a['href']
                    row[4] = chart[i].find_all('td')[3].a['href']
                except:
                    pass
                row[3] = re.sub('/movie/(.*)#tab=box-office', r'\1', row[3])
                row[4] = re.sub('/market/distributor/(.*)',   r'\1', row[4])
                for j in range(5, 11):
                    row[j] = re.sub('[(\xa0)$,%]', '', row[j])
                writer.writerow(row)
    
    print('— PROCESS COMPLETED —', '\n')
    if len(log):
        print('Timeout Errors:')
        for i, e in log:
            print('{:>7} {}'.format(i, e))

def ID(path='.'):
    """
    Scrape index of movies by year
    """
    print('Scraping index of movies by year from The Numbers...')
    sys.stdout.flush()
    
    # Calendar of Years
    URL = (
        'https://www.the-numbers.com'
        + '/movies'
    )
    try:
        soup = request(URL)
    except TimeoutError:
        return 'TimeoutError'
    calendar = [a.get_text() for a in soup.table.find_all('a', href=re.compile('year'))][::-1]
    
    # Index of Movies by Year
    URL += (
          '/year'
        + '/{}'
    )
    with open('{}/index.csv'.format(path), 'w', newline='') as file:
        writer = csv.writer(file)
        bar = ProgressBar()
        for year in bar(calendar):
            try:
                soup = request(URL.format(year))
            except TimeoutError:
                return 'TimeoutError'
            index = [a.get('href') for a in soup.table.find_all('a', href=re.compile('#tab=summary'))]
            for a in index:
                a = re.sub('/movie/(.*)#tab=summary', r'\1', a)
                writer.writerow([a])
    
    print('— PROCESS COMPLETED —', '\n')

def movies(path='.'):
    """
    Scrape movies
    """
    if not os.path.exists('{}/index.csv'.format(path)):
        ID(path)
    with open('{}/index.csv'.format(path), 'r', newline='') as file:
        index = [i for a in list(csv.reader(file)) for i in a]
    
    # Movies
    print('Scraping movies from The Numbers...')
    sys.stdout.flush()
    URL = (
        'https://www.the-numbers.com'
        + '/movie'
        + '/{}'
    )
    with open('{}/movies.csv'.format(path), 'w', newline='') as file:
        writer = csv.writer(file)
        header = [
            
            # Summary
            'title',
            'distributor',
            'release_date',
            'production_budget',
            'MPAA_rating',
            'runtime',
            'franchise',
            'keywords',
            'source',
            'genre',
            'production_method',
            'creative_type',
            'production_companies',
            'production_countries',
            
            # Box Office
            'domestic_rank',
            'domestic_gross',
            'international_rank',
            'international_gross',
            'worldwide_rank',
            'worldwide_gross',
            'close_date',
            'days_in_release',
            
            # Cast & Crew
            'actors',
            'directors',
            'producers',
            'screenwriters',
            'cinematographers',
            'composers'
        ]
        writer.writerow(header)
        bar, log = ProgressBar(), []
        for a in bar(index):
            try:
                soup = request(URL.format(a))
            except TimeoutError:
                log.append((index.index(a), a))
                continue
            
            # — Summary —
            
            # Title
            A00 = soup.h1.get_text()
            
            # Distributor
            try:
                A01 = soup.find('a', href=re.compile('^/market/distributor/')).get_text()
            except:
                A01 = str()
            
            # Movie Details
            A0X = soup.find_all('h2')
            table = None
            for e in A0X:
                if e.get_text() == 'Movie Details':
                    table = e.next_sibling.next_sibling
            try:
                A0X = [re.sub('\xa0|:', ' ', e.get_text()).strip() for e in table.find_all('td')]
                A0X = dict(zip(A0X[0::2], A0X[1::2]))
            except:
                A0X = None
            
            # Release Date
            try:
                A02 = ' '.join(A0X['Domestic Releases'].split()[:3])
                A02 = re.sub(r'(\d{1,2})\w{2},', r'\1', A02)
                A02 = datetime.strptime(A02, '%B %d %Y')
                A02 = datetime.strftime(A02, '%Y-%m-%d')
            except:
                A02 = str()
            
            # Production Budget
            try:
                A03 = re.sub('[$,]', '', A0X['Production Budget'])
            except:
                A03 = str()
            
            # MPAA Rating
            try:
                A04 = A0X['MPAA Rating'].split()[0].replace('Not', 'Not Rated')
            except:
                A04 = str()
            
            # Runtime
            try:
                A05 = re.sub('[$,]', '', A0X['Running Time']).split()[0]
            except:
                A05 = str()
            
            # Franchise
            try:
                A06 = A0X['Franchise']
            except:
                A06 = str()
            
            # Keywords
            try:
                A07 = '|'.join([e.strip() for e in A0X['Keywords'].split(',')])
            except:
                A07 = str()
            
            # Source
            try:
                A08 = A0X['Source']
            except:
                A08 = str()
            
            # Genre
            try:
                A09 = A0X['Genre']
            except:
                A09 = str()
            
            # Production Method
            try:
                A10 = A0X['Production Method']
            except:
                A10 = str()
            
            # Creative Type
            try:
                A11 = A0X['Creative Type']
            except:
                A11 = str()
            
            # Production Companies
            try:
                A12 = '|'.join([e.strip() for e in A0X['Production Companies'].split(',')])
            except:
                A12 = str()
            
            # Production Countries
            try:
                A13 = '|'.join([e.strip() for e in A0X['Production Countries'].split(',')])
            except:
                A13 = str()
            
            # — Box Office —
            
            # Theatrical Performance
            B0X = soup.find_all('h3')
            div = None
            for h3 in B0X:
                if h3.get_text() == 'Latest Ranking on Cumulative Box Office Lists':
                    div = h3.next_sibling.next_sibling
            try:
                B0X = [e.get_text() for e in div.find_all('td')]
                a, b, c = None, None, None
                for i, e in enumerate(B0X[::3]):
                    if 'for' not in e and 'Domestic' in e:
                        a = i
                    if 'for' not in e and 'International' in e:
                        b = i
                    if 'for' not in e and 'Worldwide' in e:
                        c = i
                try:
                    B00 = re.sub('[$,]', '', B0X[a * 3 + 1])  # Domestic Rank
                    B01 = re.sub('[$,]', '', B0X[a * 3 + 2])  # Domestic Gross
                except:
                    B00, B01 = str(), str()
                try:
                    B02 = re.sub('[$,]', '', B0X[b * 3 + 1])  # International Rank
                    B03 = re.sub('[$,]', '', B0X[b * 3 + 2])  # International Gross
                except:
                    B02, B03 = str(), str()
                try:
                    B04 = re.sub('[$,]', '', B0X[c * 3 + 1])  # Worldwide Rank
                    B05 = re.sub('[$,]', '', B0X[c * 3 + 2])  # Worldwide Gross
                except:
                    B04, B05 = str(), str()
            except:
                B00, B01, B02, B03, B04, B05 = [str() for i in range(6)]
            
            # Close
            B0X = soup.find_all('div', {'id': 'box_office_chart'})
            table = None
            for div in B0X:
                if len(div.find_all('a', href=re.compile('daily'))):
                    table = div
            try:
                B0X = [e.get_text() for e in table.find_all('tr')[-1].find_all('td')]
                B06 = re.sub('[ /]','-', B0X[0])  # Close Date
                B07 = re.sub('[$,]', '', B0X[7])  # Days in Release
            except:
                B06, B07 = str(), str()
            
            # — Cast & Crew —
            
            C0X = soup.find_all('div', {'id': 'cast'})
            cast, crew = None, None
            for div in C0X:
                h1 = div.h1.get_text()
                if h1 == 'Cast':
                    cast = div
                if h1 == 'Production and Technical Credits':
                    crew = div
            
            # Cast
            try:
                C00 = '|'.join([e.get_text() for e in cast.find_all('td', {'class': 'alnright'})])
            except:
                C00 = str()
            
            # Crew
            try:
                key   = [k.get_text() for k in crew.find_all('td', {'class': 'alnleft' })]
                value = [v.get_text() for v in crew.find_all('td', {'class': 'alnright'})]
                C01, C02, C03, C04, C05 = [[] for i in range(5)]
                for k, v in zip(key, value):
                    if k == 'Director':
                        C01.append(v)
                    if k == 'Producer':
                        C02.append(v)
                    if k == 'Screenwriter':
                        C03.append(v)
                    if k == 'Director of Photography':
                        C04.append(v)
                    if k == 'Composer':
                        C05.append(v)
                C01 = '|'.join(C01)  # Directors
                C02 = '|'.join(C02)  # Producers
                C03 = '|'.join(C03)  # Screenwriters
                C04 = '|'.join(C04)  # Cinematographers
                C05 = '|'.join(C05)  # Composers
            except:
                C01, C02, C03, C04, C05 = [str() for i in range(5)]
            
            row = [
                A00, A01, A02, A03, A04, A05, A06, A07,
                A08, A09, A10, A11, A12, A13, 
                B00, B01, B02, B03, B04, B05, B06, B07, 
                C00, C01, C02, C03, C04, C05
            ]
            writer.writerow(row)
    
    print('— PROCESS COMPLETED —', '\n')
    if len(log):
        print('Timeout Errors:')
        for i, e in log:
            print('{:>7} {}'.format(i, e))

def index(mode=None, path='.'):
    """
    Scrape index of movie attributes
    """
    options = {
        'distributors': [
            'gross_total',
            'ticket_count',
            'market_share'
        ],
        'franchises': [
            'domestic_gross',
            'domestic_gross_adjusted',
            'worldwide_gross',
            'year_first',
            'year_last',
            'year_count'
        ],
        'keywords': [
            'domestic_gross',
            'worldwide_gross'
        ],
        'production_companies': [
            'domestic_gross',
            'worldwide_gross'
        ],
        'production_countries': [
            'production_budget_average',
            'worldwide_gross'
        ]
    }
    if mode not in options.keys():
        raise ValueError
    print('Scraping index of movie {} from The Numbers...'.format(mode.replace('_', ' ')))
    sys.stdout.flush()
    
    URL = (
        'https://www.the-numbers.com'
        + '/{}'.format('market' if mode == 'distributors' else 'movies')
        + '/{}'.format(mode.replace('_', '-'))
    )
    try:
        soup = request(URL)
    except TimeoutError:
        return 'TimeoutError'
    path += '/features'
    if not os.path.exists(path):
        os.mkdir(path)
    with open('{}/{}.csv'.format(path, mode), 'w', newline='') as file:
        writer = csv.writer(file)
        header = [mode.replace('ies', 'y').rstrip('s'), 'movie_count']
        header.extend(options[mode])
        writer.writerow(header)
        bar, index = ProgressBar(), soup.table.find_all('tr')[1:]
        for row in bar(index):
            row = [e.get_text() for e in row.find_all('td')]
            row = row[1:] if mode == 'distributors' else row
            row[1:] = [re.sub('[(\xa0)$,%]', '', e) for e in row[1:]]
            writer.writerow(row)
    
    print('— PROCESS COMPLETED —', '\n')
