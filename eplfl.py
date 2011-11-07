from BeautifulSoup import BeautifulSoup
import re
from urllib import urlopen
import string
from pprint import PrettyPrinter


class FileMemCache:
    """Non-persistent memory cache"""

    def __init__(self):
        self._filecache = {}

    def has_key(self, key):
        return self._filecache.has_key(key)

    def fetch(self, key):
        return self._filecache[key]

    def set(self, key, value):
        self._filecache[key] = value

# Create a global cache object
filememcache = FileMemCache()


class League(object):
    """Information about a league"""

    def __init__(self, lid, exclude_teams):
        self.lid = int(lid)

        league_url = "http://fantasy.premierleague.com/my-leagues/%d/standings/"
        html = fetch_data(league_url % self.lid)
        soup = make_soup(html)

        n = soup.find("h2", {"class": "ismTabHeading"}).contents[0]
        self.name = re.sub(":\s*", "", n)

        self.teams = get_teams(soup, exclude_teams)


class LeagueStanding(object):
    """All data for a league for a particular week"""

    def __init__(self, league):
        self.league = league

        league_url = 'http://fantasy.premierleague.com/my-leagues/%d/standings/' % league.lid
        html = fetch_data(league_url)
        soup = make_soup(html)
        gw = int(re.search("Gameweek (\d+)", soup.find('caption').text).groups()[0])
        self.gameweek = gw
        self.team_standings = get_team_standings(league, soup)

    def __str__(self):
        return '%d %s gw%d' % (self.league.lid, self.league.name, self.gameweek)

    def __repr__(self):
        return '%s => ' % str(self) + ':'.join([str(x) for x in self.team_standings])

    def add_team(self, team):
        self.teams.append(team)

    def get_team_ids(self):
        vals = [x.tid for x in self.league.teams]
        return vals

    def get_team_names(self):
        vals = [x.name for x in self.league.teams]
        return vals

    def get_manager_names(self):
        vals = [x.manager for x in self.league.teams]
        return vals

    def get_gameweek_points(self):
        vals = [x.gw_score for x in self.team_standings]
        return vals

    def get_total_score(self):
        vals = [x.total_score for x in self.team_standings]
        return vals

    def get_league_ranks(self):
        vals = [x.league_rank for x in self.team_standings]
        return vals


class Team(object):
    """Information about a team"""

    def __init__(self, tid):
        self.tid = tid
        league_url = "http://fantasy.premierleague.com/entry/%d/event-history/1/"
        html = fetch_data(league_url % self.tid)
        soup = make_soup(html)

        self.name = soup.find("h2", {"class": "ismSection3"}).contents[0]
        self.manager = soup.find("h1", {"class": "ismSection2"}).contents[0]

        # find the kit colours
        kit = soup.find("input", {"id": "id_edit_entry_form-kit"})
        try:
            shirt_type = re.search("ismShirtType\":\"([^\"]+)\"", str(kit)).groups()[0]
            second_colour = re.search("ismShirt%sColor\":\"([^\"]+)\"" % string.capitalize(re.sub("s$", "", shirt_type)), str(kit)).groups()[0]
            self.colour = second_colour
        except:
            self.colour = "#333333"


class TeamStanding(object):
    """Team data for a particular game week"""

    def __init__(self, team, gw_score, total_score, league_rank):
        self.team = team
        self.gw_score = int(gw_score)
        self.total_score = int(total_score)
        self.league_rank = int(league_rank)

    def __str__(self):
        return 'Standing ob:%d' % (self.team.tid)

    def __repr__(self):
        return 'tid: %d, gameweek score: %d, total score: %d, league rank: %d' % (self.team.tid, self.gw_score, self.total_score, self.league_rank)


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
        m = re.search("href=\"\/entry\/(\d+)\/", str(team_info))
        team_id = int(m.groups()[0])

        if team_id not in exclude_teams:
            team = Team(team_id)
            teams.append(team)

    # Order team list by team id
    teams = sorted(teams, key=lambda x: x.tid)

    return teams


def get_team_standing(team, tds):
    team_league_rank = tds[1].text
    team_gw_score = tds[4].text
    team_total_score = tds[5].text

    return TeamStanding(team, team_gw_score, team_total_score, team_league_rank)


def get_team_standings(league, soup):
    indexed_teams = dict(map(lambda x: (x.tid, x), league.teams))

    table = soup.find("table", {"class": "ismTable ismStandingsTable"})
    rows = table.findAll("tr")
    # skip table header
    rows = rows[1:]

    league_data = []
    for row in rows:
        tds = row.findAll("td")
        m = re.search("href=\"\/entry\/(\d+)\/", str(tds[2]))
        team_id = int(m.groups()[0])
        if team_id in indexed_teams.keys():
            team_standing = get_team_standing(indexed_teams[team_id], tds)
            league_data.append(team_standing)

    return sorted(league_data, key=lambda x: x.team.tid)


def fetch_data(url):
    # appengine stuff
    #try:
    #   fetch_ob = fetch(url)
    #   html = fetch_ob.content
    #except:
    #    pass

    #code = fetch_ob.status_code
    #if code != 200:
    #    html = 'Failed to fetch url: %d' % code

    from md5 import md5
    cachefile = 'cache/%s' % md5(url).hexdigest()

    if filememcache.has_key(cachefile):
        return filememcache.fetch(cachefile)

    try:
        html = open(cachefile, 'r').read()
    except:
        html = urlopen(url).read()
        open(cachefile, 'w').write(html)

    filememcache.set(cachefile, html)

    return html


def make_soup(html):
    soup = BeautifulSoup(html)
    return soup


if __name__ == "__main__":
    league_url = "http://fantasy.premierleague.com/my-leagues/%d/standings/"
    my_league_id = 52875

    team_url = "http://fantasy.premierleague.com/entry/%d/event-history/%d/"
    my_team_id = 165088

    league = League(my_league_id)
    data = LeagueStanding(league)

    pp = PrettyPrinter()
    pp.pprint(data)
