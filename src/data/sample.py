#!/usr/bin/env python3
"""
Data Generator for MovieNet
"""

import csv
import datetime
import numpy as np
import os
import pandas as pd

import preprocess

def generate(mode, k=6, m=1e3, path=None, **options):
    """
    Data Generator for MovieNet
    """
    combination = Combination(mode, k, path, **options)
    
    movie = Movie(path)
    
    index, data = movie.index(), movie.data()
    
    n = data.shape[1] + 2
    
    n_X, n_Y = 1 + k * n, k
    while True:
        X, Y = np.zeros((m, n_X)), np.zeros((m, n_Y))
        for i in range(m):
            comb = next(combination)
            for j in range(k):
                a = 1 + j * n
                b = a + n - 2
                
                X[i, a : b] = data[index[comb[j]['movie_ID']]:]
                X[i, b + 1] = comb[j]['theater_count']
                X[i, b + 2] = comb[j]['in_release']
                
                Y[i, j] = comb[j]['gross']
            
            X[i, 0] = comb['date'].timetuple().tm_yday
        
        X, Y = preprocess.normalize(X, Y)
        
        yield X, Y


class Data:
    """
    Theatrical Box Office Data for MovieNet
    """
    
    # Default Directory for MovieNet Data
    path = '../../data/'
    
    def __init__(self, path=None):
        """
        Initialize Path to Directory for MovieNet Data
        """
        if os.path.isdir(str(path)):
            self.path = path


class Combination(Data):
    """
    Iterator for Sampling Random Combinations of MovieNet Data
    """
    
    def __init__(self, mode, k=6, path=None, **options):
        """
        Initialize Chart of Theatrical Box Office Competition
        """
        super().__init__(path=path)
        path = self.path + 'charts/{}.csv'.format(mode)
        
        chart = pd.read_csv(path, index_col=0, usecols=[0, 3, 5, 7, 10])
        
        for (i, v) in options.items():
            if i == 'date':
                chart = chart.loc[v['min']:v['max']]
            elif i in chart.columns:
                chart = chart.loc[chart[i].between(v['min'], v['max'])]
        
        chart.columns.values[-1] = 'in_release'
        
        self.chart = chart
        self.k = int(k)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.generate()
    
    def generate(self, k=None):
        """
        Return Random Combination of Theatrical Box Office Competition
        """
        k = self.k if k is None else int(k)
        
        n = 0
        while n < k:
            date = self.chart.sample().index[0]
            pool = self.chart.loc[date]
            n = len(pool)
        
        combination = {'date': datetime.date(*[int(a) for a in date.split('-')])}
        
        for (i, v) in enumerate(pool.sample(k).values):
            combination[i] = dict(zip(self.chart.columns, v))
        
        return combination


class Movie(Data):
    """
    Index and Attributes of Theatrical Box Office Data
    """
    
    def __init__(self, path=None):
        """
        Initialize Path to Directory for MovieNet Data
        """
        super().__init__(path=path)
        self.path += '{}.csv'
    
    def index(self):
        """
        Return Index of Movies
        """
        path = self.path.format('index')
        
        with open(path, 'r', newline='') as file:
            l = list(csv.reader(file))
        
        index = [v for _ in l for v in _]
        index = dict((v, i) for (i, v) in enumerate(index))
        
        return index
    
    def data(self):
        """
        Return Movie Attributes
        """
        path = self.path.format('movies')
        
        data = pd.read_csv(path)
        
        data = preprocess.vectorize(data)
        
        return data
