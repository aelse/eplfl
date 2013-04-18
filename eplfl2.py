import re
import requests
from BeautifulSoup import BeautifulSoup


class League(object):
    """Information about a league"""

    def __init__(self, lid, exclude_teams=[]):
        self.lid = int(lid)

        league_url = 'http://fantasy.premierleague.com/' \
                     'my-leagues/%d/standings/'
        soup = soupify(league_url % self.lid)

        n = soup.find("h2", {"class": "ismTabHeading"}).contents[0]
        self.name = str(n)

        standings = soup.find("table", {"class": "ismTable ismStandingsTable"})
        team_rows = standings.findAll("tr")[1:]
        self.teams = get_teams(soup, exclude_teams)


class Team(object):
    """Information about a team"""

    def __init__(self, tid, name, manager):
        self.tid = int(tid)
        self.name = name.rstrip().encode('utf-8')
        self.manager = manager.rstrip().encode('utf-8')

        self._points_history = None

    def __repr__(self):
        return u"<Team(%d, u'%s', u'%s')>".encode('utf-8') % \
            (self.tid, self.name, self.manager)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.manager)

    @property
    def points_history(self):
        if self._points_history:
            return self._points_history

        url = 'http://fantasy.premierleague.com/entry/%d/history/'
        soup = soupify(url % self.tid)
        table = soup.find("table", {"class": "ismTable"})

        points_history = []
        for row in table.find('tbody').findAll('tr'):
            gwp = int(row.find('td', {'class': 'ismCol2'}).contents[0])
            points_history.append(gwp)

        self._points_history = points_history
        return self._points_history


def fetch_data(url):
    r = requests.get(url)
    if not r.ok:
        raise
    return r.text


def soupify(url):
    html = fetch_data(url)
    soup = BeautifulSoup(html)
    return soup


def get_teams(soup, exclude_teams):
    """
    Retrieve a list of teams in a league.

    Pass a soup object of the league standing page.
    Information about each team in the league is fetched and
    returned in an ordered list of Team objects.
    """
    teams = []

    table = soup.find("table", {"class": "ismTable ismStandingsTable"})
    rows = table.findAll("tr")
    # skip table header
    rows = rows[1:]

    for row in rows:
        tds = row.findAll("td")
        team_info = tds[2]
        # match a unique team id
        m = re.search('href="/entry/(\d+)/', str(team_info))
        team_id = int(m.groups()[0])
        team_name = team_info.contents[0].contents[0]
        team_manager = tds[3].contents[0]

        if team_id not in exclude_teams:
            team = Team(team_id, team_name, team_manager)
            teams.append(team)

    # Order team list by team id
    teams = sorted(teams, key=lambda x: x.tid)

    return teams
