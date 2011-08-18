import eplfl
import cairo
import pycha.bar
from pprint import PrettyPrinter

def graph_gameweek_by_team(league_data):
    team_names = league_data.get_team_names()
    managers = league_data.get_manager_names()
    points = league_data.get_gameweek_points()
    title = 'Gameweek %d' % league_data.gameweek

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 400)

    dataSet = (
        ('points', [(i, l) for i, l in enumerate(points)]),
        )

    options = {
        'axis': {
            'x': {
                'ticks': [dict(v=i, label="%s - %s" % (l, managers[i])) for i, l in enumerate(team_names)],
                'label': 'Team',
                'rotate': 25,
            },
            'y': {
                'tickCount': 4,
                'rotate': 25,
                'label': 'Points'
            }
        },
        'background': {
            'chartColor': '#ffeeff',
            'baseColor': '#ffffff',
            'lineColor': '#444444'
        },
        'colorScheme': {
            'name': 'gradient',
            'args': {
                'initialColor': '#ffdf4d',
            },
        },
        'legend': {
            'hide': True,
        },
        'padding': {
            'left': 100,
            'right': 100,
            'bottom': 100,
        },
        'title': title,
    }
    chart = pycha.bar.VerticalBarChart(surface, options)
    chart.addDataset(dataSet)
    chart.render()
    surface.write_to_png('output.png')


def get_league_data(league_id):
    league_url = 'http://fantasy.premierleague.com/my-leagues/%d/standings/' % league_id

    #html = fetch_data(league_url % my_league_id)
    league_html = open("data/league_standing.html", "r").read()
    league_data = eplfl.get_league_standing(eplfl.make_soup(league_html))

    return league_data

def get_team_data(team_id, week):
    team_url = "http://fantasy.premierleague.com/entry/%d/event-history/%d/" % (team_id, week)

    #html = fetch_data(league_url % my_league_id)
    team_html = open("team_standing.html", "r").read()

if __name__ == "__main__":
    """The Steak Zone league"""
    my_league_id = 52875
    my_team_id = 165088

    league_data = get_league_data(my_league_id)
    teams = league_data.get_team_names()
    graph_gameweek_by_team(league_data)

    pp = PrettyPrinter()
    pp.pprint(teams)
