import eplfl2 as eplfl


if __name__ == '__main__':
    """Bottom 10 League Checker"""
    my_league_id = 3843
    gameweek = 25

    permitted_teams = ['New England Revolution', 'FC Dallas',
        'Portland Timbers', 'New York Red Bulls', 'Columbus Crew',
        'Philadelphia Union', 'Colorado Rapids', 'Los Angeles Galaxy']
    max_players_per_team = 2

    report = ''

    league = eplfl.League(my_league_id)

    for team in league.teams:
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
            report += 'Violations found in team {0} managed by {1}\n'.format(
                team.name, team.manager)
            report += 'http://fantasy.premierleague.com/entry/%d/event-history/%d/\n' % (team.id, gameweek)
            for violation in violations:
                report += ' - ' + violation + '\n'
            report += '\n'

    if report == '':
        report = 'No violations found for gameweek {0}'.format(gameweek)

    print report
