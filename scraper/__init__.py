import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from typing import *
from collections import defaultdict
import os

from abc import ABC, abstractmethod

'''
Removes repeated headers within the dataframe

:param tbl: the dataframe to clean
:param soup: the BeautifulSoup object of the TABLE
'''
def clean(tbl: pd.DataFrame, soup: bs) -> pd.DataFrame:
    tor = []
    for i, row in tbl.iterrows():
        for col in tbl.columns:
            if row[col] == col:
                tor.append(i)

    cols: List[bs] = soup.find('thead').find_all('th')
    cols: List[str] = list(map(lambda x: x['data-stat'], cols))
    tbl = tbl.drop(tor)

    # TODO: examine why this is fucked
    if len(tbl.columns) > len(cols):
        tbl = tbl[tbl.columns[:len(cols) - len(tbl.columns)]]

    tbl.columns = cols
    return tbl

class BBallRef:
    BASE = 'https://www.basketball-reference.com'

    '''
    Gets the table from a Basketball Reference endpoint
    
    :param endpoint: the URL endpoint ('/leagues/NBA_2019_per_game.html')
    :param table_id: the table ID of the table to fetch
    
    :returns: pandas dataframe of the table
    '''
    def get_endpoint(self, endpoint: str, table_id: str, clean_func: callable=clean, out_file: os.path.join=None,
                     separate_links=True) -> pd.DataFrame:
        # Keeps the links associated with the table
        def keep_links(df: pd.DataFrame):
            links: List[bs] = soup.find_all('td', {'class': 'left'})
            stats: DefaultDict[List] = defaultdict(list)

            for td in links:
                if td.find('a'):
                    stats[td['data-stat']].append(td.find('a')['href'])
                else:
                    stats[td['data-stat']].append('NO LINK')

            for key, val in stats.items():
                df[key + '_link'] = val

            return df

        resp = requests.get(f'{self.BASE}{endpoint}').text
        soup: bs = bs(resp).find('table', {'id': table_id})
        df = pd.read_html(resp, attrs={'id': table_id})[0]

        df = clean_func(df, soup)

        if separate_links:
            df = keep_links(df)

        if out_file:
            df.to_csv(out_file)

        return df

class AbstractPlayer(ABC, BBallRef):
    @abstractmethod
    def get_height_weight(self):
        raise NotImplementedError

    @abstractmethod
    def get_season(self, year: int = 2020):
        raise NotImplementedError

    @abstractmethod
    def get_gamelog(self, ):
        raise NotImplementedError

class AbstractPlay(ABC, BBallRef):
    pass

class AbstractGame(ABC, BBallRef):
    pass

class AbstractTeam(ABC, BBallRef):
    pass