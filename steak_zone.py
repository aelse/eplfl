import eplfl
import cairo
from pychartdir import *
from pprint import PrettyPrinter

def graph_gameweek_by_team(league_data):
    points = league_data.get_gameweek_points()
    team_names = league_data.get_team_names()
    managers = league_data.get_manager_names()
    labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    title = 'Gameweek %d' % league_data.gameweek

    colours = ['0xcc0000' for x in points]

    create_bar_chart('gameweek_by_team.png', title, points, labels, colours)

def graph_points_total(league_data):
    points = league_data.get_total_score()
    team_names = league_data.get_team_names()
    managers = league_data.get_manager_names()
    labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    title = 'Points Total at Gameweek %d' % league_data.gameweek

    colours = ['0x0000cc' for x in points]

    create_bar_chart('total_by_team.png', title, points, labels, colours)


def create_bar_chart(filename, title, values, labels, colours):
    c = XYChart(800, 400, '0xffffff', '0x000000', 1)

    c.setPlotArea(100, 20, 600, 300, '0xffffff', -1, -1, '0xdddddd')
    c.addBarLayer3(values, colours).setBorderColor(Transparent, barLighting(0.75, 2.0))
    c.xAxis().setLabels(labels).setFontAngle(-25)
    c.addTitle(title, "FreeSans.ttf", 10)
    c.makeChart(filename)

    #'initialColor': '#ffdf4d',


if __name__ == "__main__":
    """The Steak Zone league"""
    my_league_id = 52875

    league = eplfl.League(my_league_id)
    league_standing = eplfl.LeagueStanding(league)
    graph_gameweek_by_team(league_standing)
    graph_points_total(league_standing)
