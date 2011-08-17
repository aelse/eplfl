import eplfl
from pprint import PrettyPrinter

if __name__ == "__main__":
    """The Steak Zone league"""

    league_url = "http://fantasy.premierleague.com/my-leagues/%d/standings/"
    my_league_id = 52875

    team_url = "http://fantasy.premierleague.com/entry/%d/event-history/%d/"
    my_team_id = 165088

    #team_html = open("team_standing.html", "r").read()
    #html = fetch_data(league_url % my_league_id)
    league_html = open("data/league_standing.html", "r").read()
    league_data = eplfl.get_league_standing(eplfl.make_soup(league_html))

    pp = PrettyPrinter()
    pp.pprint(league_data)
