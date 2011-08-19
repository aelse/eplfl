import eplfl
import cairo
import operator
from pychartdir import *
from pprint import PrettyPrinter

colour_win   = "0x00cc00"
colour_safe  = "0x0000cc"
colour_steak = "0xcc0000"
steak_image  = "steak.png" # image from iconshock.com, free for personal use

def graph_gameweek_by_team(standing):
    points = standing.get_gameweek_points()
    team_names = standing.get_team_names()
    managers = standing.get_manager_names()
    labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    title = 'Gameweek %d' % standing.gameweek

    colours = [colour_safe for x in points]

    c = chart_boilerplate(title, labels)
    c.addBarLayer3(points, colours).setBorderColor(Transparent, barLighting(0.75, 2.0))
    c.makeChart('gameweek_by_team.png')


def graph_points_total(standing):
    team_names = standing.get_team_names()
    managers = standing.get_manager_names()
    labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    title = 'Points Total at Gameweek %d' % standing.gameweek

    # Work out the top and bottom 3 teams
    team_ids = [x.tid for x in standing.league.teams]
    points = standing.get_total_score()
    point_map = dict(zip(team_ids, points))
    low_to_high = sorted(point_map.iteritems(), key=operator.itemgetter(1))

    bottom3 = map(lambda x: x[0], low_to_high)[:3]
    top3 = map(lambda x: x[0], low_to_high)[-3:]

    # The top 3 teams are in the winner zone, bottom 3 in the steak zone
    team_order = dict(zip(team_ids, range(0,len(team_ids))))
    colours = [colour_safe for x in team_ids]
    #'initialColor': '#ffdf4d',
    for tid in bottom3:
        colours[team_order[tid]] = colour_steak
    for tid in top3:
        colours[team_order[tid]] = colour_win

    # Lucky members of the steak zone get a steak icon on their bar
    dataX = []
    dataY = []
    for tid in bottom3:
        dataX.append(team_order[tid])
        dataY.append(point_map[tid] - 5)

    c = chart_boilerplate(title, labels)
    c.addScatterLayer(dataX, dataY).getDataSet(0).setDataSymbol2(steak_image)
    c.addBarLayer3(points, colours).setBorderColor(Transparent, barLighting(0.75, 2.0))
    c.makeChart('total_by_team.png')


def chart_boilerplate(title, labels):
    c = XYChart(900, 450, '0xffffff', '0x000000', 1)

    c.setPlotArea(50, 50, 800, 300, '0xffffff', -1, -1, '0xdddddd')
    l = c.xAxis().setLabels(labels)
    l.setFontAngle(-25)
    l.setFontStyle("Numans-Regular.ttf")
    l.setPos(l.getLeftX() - 25, l.getTopY())
    c.addTitle(title, "Novecentowide-Normal.otf", 20)

    return c

    #'initialColor': '#ffdf4d',


if __name__ == "__main__":
    """The Steak Zone league"""
    my_league_id = 52875

    league = eplfl.League(my_league_id)
    league_standing = eplfl.LeagueStanding(league)
    graph_gameweek_by_team(league_standing)
    graph_points_total(league_standing)
