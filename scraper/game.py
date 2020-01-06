import requests
from typing import *

from scraper import BBallRef, AbstractGame
from scraper.play import Play, TeamType
from scraper.team import Team
from bs4 import BeautifulSoup as bs
import pandas as pd

class Game(AbstractGame):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    # TODO: Make this one nice dataframe from get_endpoint
    def get_pbp(self, out_file=None) -> List[Play]:
        endpoint = self.endpoint.replace('boxscores', 'boxscores/pbp')
        soup = bs(requests.get(f'{self.BASE}{endpoint}').text)

        team1, team2 = map(lambda x: Team(x['href']),
                           soup.find('div', {'class': 'scorebox'}).find_all('a', {'itemprop': 'name'}))

        soup = soup.find('table', {'id': 'pbp'})

        plays: List[bs] = list(filter(lambda x: not x.has_attr('class') or 'thead' not in x['class'], soup.find_all('tr')))
        # Get rid of times
        plays = [a.find_all('td') for a in plays]

        is_score = lambda x: x.getText().replace('-', '').isdigit()

        tor = []
        for time, *play in plays:
            m, s = map(float, time.getText().split(':'))
            time = m*60 + s
            if len(play) == 1:
                tor.append((time, 0, 0,  None, None, play[0]))
            else:
                score = map(int, list(map(lambda x: x.getText(), filter(is_score, play)))[0].split('-'))
                for i, a in enumerate(play):
                    if not is_score(a) and len(a) > 1:
                        if i == len(play) - 1:
                            tor.append((time, *score, TeamType.Home, team2, a))
                        else:
                            tor.append((time, *score, TeamType.Away, team1,  a))

        # # Get rid of empty cells
        # plays: List[List[bs]] = [list(filter(lambda x: len(x.getText()) != 1, a)) for a in plays]
        # # TODO: Allow to keep gametime.
        # # Get rid of score changes and game-time. Keep only the actual play data
        # plays: List[bs] = [a[0] if len(a) == 1 else list(filter(lambda x: (not x.has_attr('class') or
        #                                            'center' not in x['class']) and len(x.getText()) > 2, a))[0]
        #          for a in plays]

        # Create Play objects from soup objects
        return [Play(*a, verbose=False) for a in tor]
