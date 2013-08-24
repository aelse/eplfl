import re
import requests
from pyquery import PyQuery


def pqify(url):
    r = requests.get(url)
    if not r.ok:
        print 'Could not get url %s' % url
        raise
    pq = PyQuery(r.text)
    return pq


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
            pq = pqify(url % self.id)

            name = pq("h2.ismTabHeading").text()
            self._name = unicode(name)

            for class_ in ["ismStandingsTable", "ismAddManTable"]:
                standings = pq("table.ismTable.{0}".format(class_))
                team_rows = standings('tr')[1:]
                for row in team_rows:
                    tds = row.getchildren()
                    # Field offsets differ between tables
                    if class_ == "ismAddManTable":
                        name_idx = 0
                        info_idx = 1
                    if class_ == "ismStandingsTable":
                        name_idx = 2
                        info_idx = 3
                        # Placeholder table before first game week results are released.
                        # Skip it.
                        if tds[0].text and re.search(
                            'League standings will be updated after the next matches',
                            tds[0].text):
                            continue
                    team_name = unicode(tds[name_idx].text_content())
                    link = tds[name_idx].find('a')
                    if link is None:
                        # MLS version
                        link = tds[info_idx].find('a')
                    href = link.attrib['href']
                    m = re.search('/entry/(\d+)/', href)
                    if not m:
                        href = tds[info_idx].find('a').attrib['href']
                        m = re.search('/entry/(\d+)/', href)
                    team_id = int(m.groups()[0])
                    team_manager = unicode(tds[info_idx].text_content())
                    team = Team(team_id)
                    team._name = team_name
                    team._manager = team_manager
                    teams.append(team)

            # Look for presence of a link to the next page of results
            # to determine if we have the complete list of teams.
            page_number = page_number + 1
            if not pq('a').map(
                lambda i, x: re.search('\?le-page=%d' % page_number,
                                       x.attrib['href'])):
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
        pq = pqify(url % self.id)
        # Work out which gameweek a team was created and use that to
        # pad the list of scores with 0 for missed game weeks.
        start_week = 1
        for link in pq('a'):
            if re.match('/my-leagues/', link.get('href')):
                m = re.match('Gameweek (\d+)', link.text.strip())
                if m:
                    start_week = int(m.groups()[0])
        points_history = [0] * (start_week - 1)
        this_season_section = pq('section.ismPrimaryNarrow').children()[0]
        table = this_season_section.find('table')
        if table is not None:
            for row in table.find('tbody').getchildren():
                gwp = int(PyQuery(row).find('td.ismCol2').text())
                points_history.append(gwp)

        self._points_history = points_history
        self._manager = unicode(pq('h1.ismSection2').text())
        self._name = unicode(pq('h2.ismSection3').text())

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


class Squad(object):
    """Squad makeup for a particular team in a particular gameweek"""

    def __init__(self, team_id, gameweek):
        self.team_id = team_id
        self.gameweek = gameweek

        self._players = None

    def __repr__(self):
        return u"<Squad({0}, {1})>".format(self.team_id, self.gameweek).encode('utf-8')

    def __str__(self):
        return u"Squad {0} (gameweek {1})".format(self.team_id, self.gameweek).encode('utf-8')

    def __unicode__(self):
        return unicode(self.__str__())

    def _fill_data_fields(self):
        url = 'http://fantasy.premierleague.com/entry/%d/event-history/%d/'
        pq = pqify(url % (self.team_id, self.gameweek))

        players = []
        div = pq('div#ismTeamDisplayGraphical')
        if div:
            for player in pq('div.ismPlayerContainer'):
                team_name = player.find_class('ismShirt')[0].attrib['title']
                player_name = player.find_class('ismPitchWebName')[0].text_content().strip()
                player = Player(player_name, team_name)
                players.append(player)
        else:
            # MLS version
            table = pq('table.ismJsStatsGrouped.ismTable.ismDtTable.ismDataView')
            for row in table('tbody#ismDataElements').children():
                tds = row.findall('td')
                team_name = tds[0].find('img').get('alt')
                player_name = tds[1].text.strip()
                player = Player(player_name, team_name)
                players.append(player)
        self._players = players

        self._points_history = points_history
        self._manager = unicode(pq('h1.ismSection2').text())
        self._name = unicode(pq('h2.ismSection3').text())

    @property
    def players(self):
        if not self._players:
            self._fill_data_fields()
        return self._players


class Player(object):

    def __init__(self, player_name, team_name):
        self.player_name = player_name
        self.team_name = team_name

    def __repr__(self):
        return u"<Player('{0}', '{1}')>".format(self.player_name, self.team_name).encode('utf-8')

    def __str__(self):
        return u"{0} ({1})".format(self.player_name, self.team_name).encode('utf-8')

    def __unicode__(self):
        return unicode(self.__str__())


class LeagueStanding(object):
    """All scoring data for a League"""

    def __init__(self, league):
        self.league = league

        self._points_history = None
        self._points_total_by_gameweek = None
        self._rank_history = None
        self._score_totals = None

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

    @property
    def score_totals(self):
        if not self._score_totals:
            score_totals = []
            gw_totals = self.points_total_by_gameweek
            score_totals = dict([(team.id, self.points_total_by_gameweek[team.id][-1]) for team in self.league.teams])
            self._score_totals = score_totals
        return self._score_totals
