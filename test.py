import eplfl
import unittest
from pprint import PrettyPrinter

league_file = "data/league_standing.html"
team_file = "data/team_standing.html"


class Soupification(unittest.TestCase):
    league_html = open(league_file, "r").read()
    team_html = open(team_file, "r").read()

    def testParseTeamStanding(self):
        """must parse team standing"""
        soup = eplfl.make_soup(self.team_html)

    def testParseLeagueStanding(self):
        """must parse league standing"""
        soup = eplfl.make_soup(self.league_html)


class LeagueStanding(unittest.TestCase):
    league_html = open(league_file, "r").read()
    soup = eplfl.make_soup(league_html)

    def testGetLeagueStanding(self):
        """extract league data"""
        league_standing = eplfl.get_league_standing(self.soup)


if __name__ == "__main__":
    unittest.main()
