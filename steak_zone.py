import eplfl
import cairo
import operator
import csv
import sys
from pychartdir import *
from pprint import PrettyPrinter

colour_win   = "0x00cc00"
colour_safe  = "0x0000cc"
colour_steak = "0xcc0000"
steak_image  = "steak.png" # image from iconshock.com, free for personal use
label_font = "Numans-Regular.ttf"
title_font = "Avenir LT 65 Medium.ttf"

def graph_gameweek_by_team(standing):
    points = standing.get_gameweek_points()
    team_names = standing.get_team_names()
    managers = standing.get_manager_names()
    labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    y_label = "Points"
    title = 'Gameweek %d Accumulated Points' % standing.gameweek

    colours = [colour_safe for x in points]

    c = chart_boilerplate(title, labels, y_label)
    c.addBarLayer3(points, colours).setBorderColor(Transparent, barLighting(0.75, 2.0))
    c.makeChart('gameweek_by_team.png')


def graph_points_total_at_gameweek(standing):
    team_names = standing.get_team_names()
    managers = standing.get_manager_names()
    labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    y_label = "Points"
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

    c = chart_boilerplate(title, labels, y_label)
    c.addScatterLayer(dataX, dataY).getDataSet(0).setDataSymbol2(steak_image)
    c.addBarLayer3(points, colours).setBorderColor(Transparent, barLighting(0.75, 2.0))
    c.makeChart('total_by_team.png')


def graph_points_history(standing, history, title, filename):
    # number of weeks the game runs for
    num_weeks = 38
    labels = [''] * 2 + ['%d' % x for x in range(1, num_weeks + 1)]
    y_label = 'Points'
    x_label = 'Gameweek'

    team_names = standing.get_team_names()
    managers = standing.get_manager_names()
    line_labels = ['%s\n%s' % (team_names[i], managers[i]) for i, x in enumerate(team_names)]
    name_map = dict(zip(standing.get_team_ids(), team_names))

    c = chart_boilerplate(title, labels, y_label)
    c.xAxis().setTitle(x_label)
    c.addLegend(50, 390, 0, label_font, 8).setBackground(Transparent)

    layer = c.addLineLayer2()
    for k in history.keys():
        # Possible gaps in points data will have a value of 0, which we
        # replace with NoValue so ChartDirector handles them nicely.
        # We make the fair assumption that no team actually scored 0
        # in a game week.
        history[k] = [0] + map(lambda x: x if x else NoValue, history[k])

        layer.addDataSet(history[k], -1, name_map[k])

    c.makeChart(filename)


def chart_boilerplate(title, labels, y_label):
    c = XYChart(900, 450, '0xffffff', '0x000000', 1)

    c.setPlotArea(50, 50, 800, 300, '0xffffff', '0xf8f8f8', Transparent, c.dashLineColor('0xcccccc', DotLine), c.dashLineColor('0xcccccc', DotLine))
    l = c.xAxis().setLabels(labels)
    l.setFontAngle(-25)
    l.setFontStyle(label_font)
    l.setPos(l.getLeftX() - 25, l.getTopY())
    c.addTitle(title, title_font, 20)
    c.yAxis().setTitle(y_label)

    return c

    #'initialColor': '#ffdf4d',

def load_points_history(filename):
    points_history = {}
    try:
        f = open(filename, 'rb')
        r = csv.reader(f, delimiter=',', quotechar='"')
        for row in r:
            data = row # row not iterable
            data = map(lambda x: int(x), data)
            tid = data[0]
            points = data[1:]
            points_history[tid] = points
        f.close()
    except:
        # If points file can't be accessed, bail out to avoid
        # potentially destructive operation when it is overwritten
        print 'Could not read %s' % filename
        print 'Please \'touch %s\' and run this script again' % filename
        sys.exit(1)

    return points_history


def write_points_history(filename, points):
    # convert dictionary into a list with key as first element
    flat_history = []
    for k, p in points.items():
        flat_history.append([k] + p)

    try:
        f = open(filename, 'wb')
        w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in flat_history:
            w.writerow(row)
        f.close()
    except:
        print 'Could not write %s' % filename


def update_points_history(savefile, gameweek, points):
    history = load_points_history(savefile)

    for k, p in points.items():
        # May be a team we have not yet recorded
        if not history.has_key(k):
            history[k] = []
        # May be some gameweeks with no recorded stats for a team
        if len(history[k]) < gameweek:
            history[k].extend([0] * (gameweek - len(history[k])))
        # Update current gameweek points
        history[k][gameweek - 1] = p

    write_points_history(savefile, history)


if __name__ == "__main__":
    """The Steak Zone league"""
    my_league_id = 52875

    league = eplfl.League(my_league_id)
    league_standing = eplfl.LeagueStanding(league)

    savefile = 'data/gameweek_points_history.csv'
    update_points_history(savefile, league_standing.gameweek, dict(zip([x.tid for x in league.teams], league_standing.get_gameweek_points())))
    history = load_points_history(savefile)
    graph_points_history(league_standing, history, 'Gameweek Points History', 'gameweek_points_history.png')

    savefile = 'data/total_points_history.csv'
    update_points_history(savefile, league_standing.gameweek, dict(zip([x.tid for x in league.teams], league_standing.get_total_score())))
    history = load_points_history(savefile)
    graph_points_history(league_standing, history, 'Total Points History', 'total_points_history.png')

    savefile = 'data/rank_history.csv'
    update_points_history(savefile, league_standing.gameweek, dict(zip([x.tid for x in league.teams], league_standing.get_league_ranks())))

    graph_gameweek_by_team(league_standing)
    graph_points_total_at_gameweek(league_standing)
