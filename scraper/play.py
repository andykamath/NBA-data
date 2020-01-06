from scraper import BBallRef, AbstractPlayer, AbstractPlay, AbstractTeam
from bs4 import BeautifulSoup as bs
import re

import enum

class PlayType(enum.Enum):
    JumpBall = 'Jump Ball'
    Turnover = 'Turnover'
    Rebound = 'Rebound'
    Foul = 'Foul'
    Shot = 'Shot'
    EndQuarter = 'End of Quarter'
    FreeThrow = 'Free Throw'
    Substitution = 'Substitution'
    Other = 'Other'
    Timeout = 'Timeout'
    Violation = 'Violation'
    StartQuarter = 'Start of Quarter'
    Ejection = 'Ejection'

    def __str__(self):
        return self.value

class TeamType(enum.Enum):
    Away = 'Away'
    Home = 'Home'

    def __str__(self):
        return self.value

class Play(AbstractPlay):
    team: AbstractTeam = None
    p1: AbstractPlayer = None
    p2: AbstractPlayer = None
    p3: AbstractPlayer = None
    score_diff: int = 0
    t1_score: int = 0
    t2_score: int = 0
    team_play: TeamType = None

    secs_left: int
    player: callable
    play_type: PlayType
    desc: str
    team_type: TeamType

    '''
    :type: PlayType.JumpBall
    :desc: "Jump Ball"
    :score_diff: 0
    :p1: Center 1
    :p2: Center 2
    :p3: Player receiving the ball
    '''
    def JumpBall(self, action: bs):
        # print(action)
        self.play_type = PlayType.JumpBall
        ps = list(map(lambda x: self.player(x['href']), action.find_all('a')))
        if len(ps) == 1:
            self.p1 = ps[0]
        if len(ps) == 2:
            self.p1, self.p2 = ps
        if len(ps) == 3:
            self.p1, self.p2, self.p3 = ps
        self.desc = 'Jump Ball'

    '''
    :type: PlayType.FreeThrow
    :desc: "makes/misses free throw 1 of 1", etc.
    :score_diff: 0-1
    :p1: Player shooting the free throw
    '''
    def FreeThrow(self, action: bs):
        self.play_type = PlayType.FreeThrow
        self.p1 = self.player(action.find('a')['href'])
        [s.extract() for s in action('a')]
        self.desc = action.getText().strip()
        if ' ma' in action.getText():
            self.score_diff = 1

    '''
    :type: PlayType.Shot
    :desc: "makes$2-pt$jump shot$8" (using dollar signs to separate make/miss, point, shot type, distance)
    :score_diff: 0-3
    :p1: Player making/missing the shot
    :p2: Player assisting/blocking
    '''
    def Shot(self, action: bs):
        self.play_type = PlayType.Shot
        self.p1 = self.player(action.find_all('a')[0]['href'])
        if len(action.find_all('a')) > 1:
            self.p2 = self.player(action.find_all('a')[1]['href'])

        # Remove parentheses (assists, blocks)
        new_str = str(action)
        start = new_str.find('(')
        end = new_str.find(')')
        if start != -1 and end != -1:
            new_str = new_str.replace(new_str[start:end + 1], '')

        action = bs(new_str, "lxml").find('td')

        # Remove player tags
        [s.extract() for s in action('a')]
        self.desc: str = action.getText().strip()
        self.desc = self.desc.replace('makes ', 'makes$')\
            .replace('misses ', 'misses$')\
            .replace(' from ', '$')\
            .replace(' at ', '$')\
            .replace("-pt", '-pt$')\
            .replace(' ft', '')
        self.desc = '$'.join([a.strip() for a in self.desc.split('$')])

        make, point, _, _ = self.desc.split('$')
        if make == 'makes':

            self.score_diff = int(point[0])

    '''
    :type: PlayType.Rebound
    :desc: "Offensive Rebound" or "Defensive Rebound"s
    :score_diff: 0
    :p1: Player getting the rebound
    '''
    def Rebound(self, action: bs):
        self.play_type = PlayType.Rebound
        if 'by Team' not in str(action):
            self.p1 = self.player(action.find('a')['href'])
        self.desc = action.getText().split(' by ')[0].strip()

    '''
    :type: PlayType.Foul
    :desc: "Shooting Foul" or "Offensive Foul", etc.
    :score_diff: 0
    :p1: Player fouling
    :p2: Player drawing the foul
    '''
    def Foul(self, action: bs):
        self.play_type = PlayType.Foul
        self.desc = action.getText().split(' by ')[0].strip()
        players = action.find_all('a')
        if len(players) > 0:
            self.p1 = self.player(players[0]['href'])
        if len(players) > 1:
            self.p2 = self.player(players[1]['href'])

    '''
    :type: PlayType.Turnover
    :desc: "Turnover" or "Steal; bad pass", etc.
    :score_diff: 0
    :p1: Player turning the ball over
    :p2: Player causing the ball to be turned over
    '''
    def Turnover(self, action: bs):
        self.play_type = PlayType.Turnover
        players = action.find_all('a')
        if len(players) > 0:
            self.p1 = self.player(players[0]['href'])
        if len(players) > 1:
            self.p2 = self.player(players[1]['href'])

        new_str = str(action)
        start = new_str.find('(')
        end = new_str.find(')')
        if start != -1 and end != -1:
            self.desc = new_str[start + 1 : end]
            if ' by ' in self.desc:
                self.desc = self.desc.split(' by ')[0].strip()
        else:
            self.desc = 'Turnover'

    '''
    :type: PlayType.Timeout
    :desc: "New Orleans full timeout"
    :score_diff: 0
    '''
    def Timeout(self, action: bs):
        self.desc = action.getText()
        self.play_type = PlayType.Timeout

    '''
    :type: PlayType.Substitution
    :desc: Substitution
    :score_diff: 0
    :p1: Player Entering
    :p2: Player Leaving
    '''
    def Substition(self, action: bs):
        self.play_type = PlayType.Substitution
        self.desc = 'Substitution'
        self.p1, self.p2 = map(lambda x: self.player(x['href']), action.find_all('a'))

    '''
    :type: PlayType.Violation
    :desc: "Violation by Team"
    :score_diff: 0
    :p1: Player causing the violation
    '''
    def Violation(self, action: bs):
        self.play_type = PlayType.Violation
        if action.find('a'):
            self.p1 = self.player(action.find('a')['href'])
        new_str = str(action)
        start = new_str.find('(')
        end = new_str.find(')')
        if start != -1 and end != -1:
            self.desc = new_str[start + 1: end]
        else:
            self.desc = 'Team Violation'

    '''
    :type: PlayType.StartQuarter
    :desc: "Start of 1st Quarter"
    :score_diff: 0
    '''
    def StartQuarter(self, action: bs):
        self.play_type = PlayType.StartQuarter
        self.desc = action.getText()

    '''
    :type: PlayType.EndQuarter
    :desc: "End of 1st Quarter"
    :score_diff: 0
    '''

    def EndQuarter(self, action: bs):
        self.play_type = PlayType.EndQuarter
        self.desc = action.getText()

    '''
    :type: PlayType.Ejection
    :desc: "Ejected from game"
    :score_diff: 0
    :p1: the player to be ejected
    '''

    def Ejection(self, action: bs):
        self.desc = "Ejected from game"
        self.play_type = PlayType.Ejection
        self.p1 = self.player(action.find('a')['href'])

    def __init__(self, secs_left: int, t1_score: int, t2_score: int, team_play: TeamType,
                 team: AbstractTeam, action: bs, verbose=True):
        self.secs_left = secs_left
        self.team = team
        self.t1_score = t1_score
        self.t2_score = t2_score
        self.team_play = team_play

        self.raw = action

        if verbose:
            print(str(action))

        from scraper.player import Player
        self.player = Player

        if 'Jump ball' in str(action):
            self.JumpBall(action)

        elif ' rebound ' in str(action):
            self.Rebound(action)

        elif ' free throw' in str(action):
            self.FreeThrow(action)

        elif ' makes ' in str(action) or ' misses ' in str(action):
            self.Shot(action)

        elif ' foul ' in str(action):
            self.Foul(action)

        elif 'Turnover by ' in str(action):
            self.Turnover(action)

        elif ' enters the game for ' in str(action):
            self.Substition(action)

        elif ' timeout' in str(action):
            self.Timeout(action)

        elif 'Violation by ' in str(action):
            self.Violation(action)

        elif 'End of ' in str(action):
            self.EndQuarter(action)

        elif 'Start of ' in str(action):
            self.StartQuarter(action)

        elif ' ejected ' in str(action):
            self.Ejection(action)

        elif 'Instant Replay' in str(action):
            self.desc = action.getText()
            self.play_type = PlayType.Other

        if verbose:
            print(str(self))

    def __str__(self):
        return f'{self.secs_left} {self.team} +{self.score_diff}: ({self.t1_score}-{self.t2_score}) ' \
               f'{self.play_type} ({self.desc}) - {self.p1}, {self.p2}, {self.p3}'

