from scraper import BBallRef
from scraper.player import Player
from scraper.game import Game
import os

# df = BBallRef.get_endpoint('/leagues/NBA_2020_advanced.html', 'advanced_stats', out_file=os.path.join('output', 'advanced.csv'))
# biostats = []
# for href in df['player_link']:
#     print(href)
#     player = Player(href)
#     biostats.append(player.get_height_weight())
#
# df['height'], df['weight'] = zip(*biostats)
# df.to_csv('output/biostats_per_poss.csv')

PG = Player('/players/g/georgpa01.html')
for play in PG.get_gamelog()[0].get_pbp('output/gamelog.csv'):
    print(play)