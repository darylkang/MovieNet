#!/usr/bin/env python3
"""
Web Scraping for MovieNet
"""

import os
import sys

from argparse import ArgumentParser

import box_office_mojo
import the_numbers

def main(args, options):
    """
    Web Scraping for MovieNet
    """
    mode, path = args.mode, args.path
    if not os.path.isdir(path):
        print("OSError: '{}' is not a valid path".format(path))
        sys.exit()
    if 'all' in mode:
        mode.extend(options.keys())
        mode.remove('all')
    elif 'features' in mode:
        mode.extend([k for k, v in options.items() if v['type'] == 'reference'])
        mode.remove('features')
    modes = list(set(mode))
    if 'movies' in mode and 'index' in mode:
        modes.remove('index')
    modes.sort()
    for mode in modes:
        if mode == 'charts':
            the_numbers.scrape.charts('weekend', path)
        elif mode == 'index':
            the_numbers.scrape.ID(path)
        elif mode == 'movies':
            the_numbers.scrape.movies(path)
        elif mode in [k for k, v in options.items() if v['source'] == 'box_office_mojo']:
            box_office_mojo.scrape.index(mode, path)
        else:
            the_numbers.scrape.index(mode, path)
    sys.exit()

if __name__ == '__main__':
    """
    Run program from the command line
    """
    parser = ArgumentParser(
        prog='scrape.py',
        usage='%(prog)s [-h] MODE [MODE ...] [-p PATH]',
        description='Web Scraping for MovieNet',
        epilog='Copyright © 2018 Daryl Kang'
    )
    options = {
        'actors':               {'source': 'box_office_mojo', 'type': 'reference'},
        'charts':               {'source': 'the_numbers',     'type': 'metadata' },
        'cinematographers':     {'source': 'box_office_mojo', 'type': 'reference'},
        'composers':            {'source': 'box_office_mojo', 'type': 'reference'},
        'directors':            {'source': 'box_office_mojo', 'type': 'reference'},
        'distributors':         {'source': 'the_numbers',     'type': 'reference'},
        'franchises':           {'source': 'the_numbers',     'type': 'reference'},
        'index':                {'source': 'the_numbers',     'type': 'metadata' },
        'keywords':             {'source': 'the_numbers',     'type': 'reference'},
        'movies':               {'source': 'the_numbers',     'type': 'master'   },
        'producers':            {'source': 'box_office_mojo', 'type': 'reference'},
        'production_companies': {'source': 'the_numbers',     'type': 'reference'},
        'production_countries': {'source': 'the_numbers',     'type': 'reference'},
        'screenwriters':        {'source': 'box_office_mojo', 'type': 'reference'}
    }
    choices = ['all', 'features']
    choices.extend(options)
    
    parser.add_argument(
        'mode',
        nargs='*',
        choices=choices,
        help='choose from {}'.format(', '.join("'{}'".format(mode) for mode in options)),
        metavar='MODE'
    )
    parser.add_argument(
        '-p', '--path',
        default='.',
        help="specify the output directory (default: '.')"
    )
    args = parser.parse_args()
    
    main(args, options)
