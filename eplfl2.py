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


class LeagueStanding(object):
    """All scoring data for a League"""

    def __init__(self, league):
        self.league = league

        self._points_history = None
        self._points_total_by_gameweek = None
        self._rank_history = None

    @property
    def points_history(self):
        if not self._points_history:
            points_history = {}
            for team in self.league.teams:
                points_history[team.tid] = team.points_history
            self._points_history = points_history
        return self._points_history

    @property
    def points_total_by_gameweek(self):
        if not self._points_total_by_gameweek:
            points_total_by_gameweek = {}
            for team in self.league.teams:
                points_total = []
                total = 0
                for points in self.points_history[team.tid]:
                    total += points
                    points_total.append(total)
                points_total_by_gameweek[team.tid] = points_total
            self._points_total_by_gameweek = points_total_by_gameweek
        return self._points_total_by_gameweek

    @property
    def rank_history(self):
        if not self._rank_history:
            rank_history = {}
            totals = self.points_total_by_gameweek
            num_gameweeks = len(totals.items()[0][1])
            for gw in xrange(0, num_gameweeks):
                gw_totals = map(lambda x: (x, totals[x][gw]), totals.keys())
                ordered = sorted(gw_totals, key=lambda x: x[1], reverse=True)
                for rank, tupl in enumerate(ordered, 1):
                    try:
                        rank_history[tupl[0]].append(rank)
                    except KeyError:
                        rank_history[tupl[0]] = [rank]
            self._rank_history = rank_history
        return self._rank_history


def soupify(url):
    r = requests.get(url)
    if not r.ok:
        raise
    soup = BeautifulSoup(r.text)
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
