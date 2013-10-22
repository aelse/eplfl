import eplfl
import unicodedata


if __name__ == '__main__':
    """Bottom 10 League Checker"""
    my_league_id = 235981
    import sys
    gameweek = int(sys.argv[1])

    permitted_teams = ['Aston Villa', 'Cardiff City', 'Crystal Palace',
                       'Fulham', 'Hull City', 'Norwich', 'Newcastle',
                       'Southampton', 'Stoke City', 'Sunderland']
    max_players_per_team = 2

    report = u''

    league = eplfl.League(my_league_id)

    for team in league.teams:
        try:
            squad = eplfl.Squad(team.id, gameweek)

            teams = {}
            for player in squad.players:
                try:
                    teams[player.team_name] += 1
                except KeyError:
                    teams[player.team_name] = 1

            violations = []
            for team_name, player_count in teams.items():
                if team_name not in permitted_teams:
                    violations.append(
                        'Player found from unsanctioned team {0}'.format(team_name))
                if player_count > max_players_per_team:
                    violations.append(
                        'Squad contains {0} players from {1}'.format(
                        player_count, team_name))
            if violations:
                t_manager = unicodedata.normalize('NFKD', team.manager).encode('ascii', 'ignore')
                t_name = unicodedata.normalize('NFKD', team.name).encode('ascii', 'ignore')
                line = 'Violations found in team {0} managed by {1}\n'.format(
                    t_name, t_manager)
                report += 'Violations found in team {0} managed by {1}\n'.format(
                    t_name, t_manager)
                report += 'http://fantasy.premierleague.com/entry/%d/event-history/%d/\n' % (team.id, gameweek)
                for violation in violations:
                    report += ' - ' + violation + '\n'
                report += '\n'
        except:
            print 'Exception on team id %d' % team.id

    if report == '':
        report = 'No violations found for gameweek {0}'.format(gameweek)

    print report
