from BeautifulSoup import BeautifulSoup
import re
from urllib import urlopen
from pprint import PrettyPrinter

class LeagueWeek(object):
    """All data for a league for a particular week"""

    def __init__(self, lid, name, gameweek):
        self.lid = int(lid)
        self.name = name
        self.gameweek = int(gameweek)
        self.teams = []

    def __str__(self):
        return '%d %s gw%d' % (self.lid, self.name, self.gameweek)

    def __repr__(self):
        return '%s => ' % str(self) + ':'.join([str(x) for x in self.teams])

    def add_team(self, team):
        self.teams.append(team)

    def get_team_ids(self):
        vals = [x.tid for x in self.teams]
        return vals

    def get_team_names(self):
        vals = [x.name for x in self.teams]
        return vals

    def get_manager_names(self):
        vals = [x.manager for x in self.teams]
        return vals

    def get_gameweek_points(self):
        vals = [x.gw_score for x in self.teams]
        return vals

    def get_total_score(self):
        vals = [x.total_score for x in self.teams]
        return vals


class TeamWeek(object):
    """Team data for a particular game week"""

    def __init__(self, tid, name, manager, gw_score, total_score, league_rank):
        self.tid = int(tid)
        self.name = name
        self.manager = manager
        self.gw_score = int(gw_score)
        self.total_score = int(total_score)
        self.league_rank = int(league_rank)

    def __str__(self):
        return '%d %s' % (self.tid, self.name)

    def __repr__(self):
        return 'tid: %d, name: %s, manager: %s, gameweek score: %d, total score: %d, league rank: %d' % (self.tid, self.name, self.manager, self.gw_score, self.total_score, self.league_rank)


def get_team_standing(row):
    tds = row.findAll("td")

    # some image, rank, team info, manager, gameweek score, total score
    team_league_rank = tds[1].text
    team_info = tds[2]
    team_manager = tds[3].text
    team_gw_score = tds[4].text
    team_total_score = tds[5].text

    # match a unique team id
    m = re.search("href=\"\/entry\/(\d+)\/", str(team_info))
    team_id = m.groups()[0]
    team_name = team_info.text

    return TeamWeek(team_id, team_name, team_manager, team_gw_score, team_total_score, team_league_rank)


def get_league_standing(soup):
    gw = int(re.search("Gameweek (\d+)", soup.find('caption').text).groups()[0])

    league_data = LeagueWeek(123, 'The Steak Zone', gw)
    
    table = soup.find("table", {"class": "ismTable ismStandingsTable"})
    #print table.prettify()
    rows = table.findAll("tr")

    # skip table header
    rows = rows[1:]

    for row in rows:
        team_data = get_team_standing(row)
        league_data.add_team(team_data)

    return league_data


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

    html = urlopen(url).read()
    return html


def make_soup(html):
    soup = BeautifulSoup(html)
    return soup


if __name__ == "__main__":
    league_url = "http://fantasy.premierleague.com/my-leagues/%d/standings/"
    my_league_id = 52875

    team_url = "http://fantasy.premierleague.com/entry/%d/event-history/%d/"
    my_team_id = 165088

    #html = open('data/league_standing.html', 'r').read()
    html = fetch_data(league_url % my_league_id)

    soup = make_soup(html)
    data = get_league_standing(soup)

    pp = PrettyPrinter()
    pp.pprint(data)
