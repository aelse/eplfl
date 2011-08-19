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


def graph_points_total_at_gameweek(standing):
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
    #c.addTitle(title, "Novecentowide-Normal.otf", 20)
    c.addTitle(title, "Avenir LT 65 Medium.ttf", 20)

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


def update_points_history(gameweek, points):
    savefile = 'points_history.csv'
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

    update_points_history(league_standing.gameweek, dict(zip([x.tid for x in league.teams], league_standing.get_gameweek_points())))

    graph_gameweek_by_team(league_standing)
    graph_points_total_at_gameweek(league_standing)
