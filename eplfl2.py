import re
import requests
from BeautifulSoup import BeautifulSoup


class League(object):
    """Information about a league"""

    def __init__(self, id_):
        self.id = int(id_)
        self._name = None
        self._teams = None

    def _fill_data_fields(self):
        league_url = 'http://fantasy.premierleague.com/my-leagues/%d/standings/'
        page_number = 1
        more_pages = True

        teams = []
        while more_pages:
            url = league_url + '?le-page=%d' % page_number
            soup = soupify(url % self.id)

            name = soup.find("h2", {"class": "ismTabHeading"}).contents[0]
            self._name = unicode(name)

            for class_ in ["ismStandingsTable", "ismAddManTable"]:
                standings = soup.find("table", {"class": "ismTable {0}".format(class_)})
                team_rows = standings.findAll("tr")[1:]
                for row in team_rows:
                    tds = row.findAll('td')
                    # Field offsets differ between tables
                    if class_ == "ismAddManTable":
                        name_idx = 0
                        info_idx = 1
                    if class_ == "ismStandingsTable":
                        name_idx = 2
                        info_idx = 3
                        # Placeholder table before first game week results are released.
                        # Skip it.
                        if re.search('League standings will be updated after the next matches',
                            str(tds[0].contents[0])):
                            continue
                    team_name = tds[name_idx].contents[0]
                    team_info = tds[info_idx].contents[0]
                    m = re.search('href="/entry/(\d+)/', str(team_info))
                    team_id = int(m.groups()[0])
                    team_manager = team_info.contents[0]
                    team = Team(team_id)
                    team._name = team_name
                    team._manager = team_manager
                    teams.append(team)

            # Look for presence of a link to the next page of results
            # to determine if we have the complete list of teams.
            page_number = page_number + 1
            if not soup.find(href=re.compile('\?le-page=%d' % page_number)):
                more_pages = False

        # Order team list by team id
        self._teams = sorted(teams, key=lambda x: x.id)

    def __repr__(self):
        return u"<League({0})>".format(self.id).encode('utf-8')

    def __str__(self):
        return u"{0})".format(self.name).encode('utf-8')

    def __unicode__(self):
        return unicode(self.__str__())

    @property
    def name(self):
        if not self._name:
            self._fill_data_fields()
        return self._name

    @property
    def teams(self):
        if not self._teams:
            self._fill_data_fields()
        return self._teams


class Team(object):
    """Information about a team"""

    def __init__(self, id_):
        self.id = int(id_)
        self._points_history = None
        self._name = None
        self._manager = None

    def __repr__(self):
        return u"<Team({0})>".format(self.id).encode('utf-8')

    def __str__(self):
        return u"{0} ({1})".format(self.name, self.manager).encode('utf-8')

    def __unicode__(self):
        return unicode(self.__str__())

    def _fill_data_fields(self):
        url = 'http://fantasy.premierleague.com/entry/%d/history/'
        soup = soupify(url % self.id)

        points_history = []
        this_season_header = soup.find(text=re.compile(r'This Season'))
        section = this_season_header.parent.parent
        table = section.find("table", {"class": "ismTable"})
        if table:
            for row in table.find('tbody').findAll('tr'):
                gwp = int(row.find('td', {'class': 'ismCol2'}).contents[0])
                points_history.append(gwp)

        self._points_history = points_history
        self._manager = unicode(soup.find('h1', {'class': 'ismSection2'}).contents[0])
        self._name = unicode(soup.find('h2', {'class': 'ismSection3'}).contents[0])

    @property
    def points_history(self):
        if not self._points_history:
            self._fill_data_fields()
        return self._points_history

    @property
    def name(self):
        if not self._name:
            self._fill_data_fields()
        return self._name

    @property
    def manager(self):
        if not self._manager:
            self._fill_data_fields()
        return self._manager


class LeagueStanding(object):
    """All scoring data for a League"""

    def __init__(self, league):
        self.league = league

        self._points_history = None
        self._points_total_by_gameweek = None
        self._rank_history = None

    def get_team_ids(self):
        return [x.id for x in self.league.teams]

    def get_team_names(self):
        return [x.name for x in self.league.teams]

    def get_manager_names(self):
        return [x.manager for x in self.league.teams]

    def get_gameweek_points(self):
        return [x.points_history[-1] for x in self.league.teams]

    @property
    def gameweek(self):
        return len(self.points_history.items()[0][1])

    @property
    def points_history(self):
        if not self._points_history:
            points_history = {}
            for team in self.league.teams:
                points_history[team.id] = team.points_history
            self._points_history = points_history
        return self._points_history

    @property
    def points_total_by_gameweek(self):
        if not self._points_total_by_gameweek:
            points_total_by_gameweek = {}
            for team in self.league.teams:
                points_total = []
                total = 0
                for points in self.points_history[team.id]:
                    total += points
                    points_total.append(total)
                points_total_by_gameweek[team.id] = points_total
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
