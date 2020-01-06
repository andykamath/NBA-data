from scraper import AbstractTeam

class Team(AbstractTeam):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def __str__(self):
        return self.endpoint.split('/')[-2]