from scraper import BBallRef, AbstractPlayer
from scraper.game import Game

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from typing import *
import os

class Player(AbstractPlayer):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.id = endpoint.split('/')[-1].replace('.html', '')

    '''
    Gets the height and weight of a player
    '''
    def get_height_weight(self) -> Tuple[int, int]:
        print(self.endpoint)
        soup: bs = bs(requests.get(self.BASE+self.endpoint).text)
        self.height_ft, self.height_in = map(int, soup.find('span', {'itemprop': 'height'}).text.split('-'))
        self.weight = int(soup.find('span', {'itemprop': 'weight'}).text[:-2])

        return self.height_ft * 12 + self.height_in, self.weight

    '''
    Get season
    '''
    def get_season(self, year: int=2020):
        endpoint = self.endpoint.replace('.html', '')
        url = f'{endpoint}/gamelog/{year}'

        tbl = self.get_endpoint(url, 'pgl_basic', separate_links=True)
        return tbl

    '''
    Get games participated in
    
    :param year: the season to get
    :returns: endpoints to the games the player participated in
    '''
    def get_gamelog(self, year: int=2020) -> List[Game]:
        def hasint(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        links = self.get_season(year)

        # Filter active games and get game links
        links = list(map(Game, links.loc[links['fg'].apply(hasint)]['date_game_link']))
        return links

    def __str__(self):
        return self.endpoint.split('/')[-1].replace('.html', '')

    def __eq__(self, other):
        if isinstance(other, Player):
            return other.endpoint == self.endpoint
        return False