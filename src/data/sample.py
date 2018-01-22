#!/usr/bin/env python3
"""
Data Generator for MovieNet
"""

import datetime
import pandas as pd
import random

def generate(mode, pool_size=6, **options):
    """
    Generate random combinations of theatrical box office competition
    """
    try:
        path = options['path'] + mode + '.csv'
    except:
        path = '../../../data/charts/' + mode + '.csv'
    
    chart = pd.read_csv(path, index_col=0, usecols=[0, 3, 5, 7, 10])
    
    for k, v in options.items():
        if k == 'date':
            chart = chart.loc[v['min']:v['max']]
        elif k in chart.columns:
            chart = chart.loc[chart[k].between(v['min'], v['max'])]
    
    while True:
        date = chart.index[random.randrange(len(chart))]
        pool = chart.loc[date]
        
        n = len(pool)
        if n < pool_size:
            continue
        
        sample = {'date': datetime.date(*[int(a) for a in date.split('-')])}
        
        for i, e in enumerate(random.sample(range(n), pool_size)):
            sample[i] = {j: pool.iloc[e][j] for j in chart.columns}
        
        yield sample
