import games_generation as gg
import pandas as pd
import numpy as np


def get_aggregate_data(games):
    """
    Function to check the quality of a list of games (e.g. from the output of get_game_list or get_best_match)

    :param games: (pd.DataFrame) list of games
    :return: (pd.DataFrame) number of games played by each team on each field
    """
    dfhome = games[['home','field']]
    dfaway = games[['away','field']]
    dfaway.columns=['home','field']
    dfagg = dfhome.append(dfaway).reset_index()
    dfagg = dfagg[np.isnan(dfagg.field)==False].groupby(['home','field']).count()
    return(dfagg)


def get_schedule(games):
    """
    Generate a random yet consistent schedule

    :param games: (pd.DataFrame) list of games
    :return: (pd.DataFrame) list of games with a time slot for each game
    """
    games['timeslot'] = np.nan
    timeslot = 0
    # Loop until each game has a slot on the schedule
    while sum(np.isnan(games['timeslot']))>0:
        timeslot+=1
        teams_playing = []
        fields_taken = []
        games = games.sample(frac=1).reset_index(drop=True)     # shuffle rows
        for row in range(games.shape[0]):
            if np.isnan(games.timeslot[row]):
                teams = [games['home'][row], games['away'][row]]
                field = games['field'][row]
                if not any(i in teams for i in teams_playing) and field not in fields_taken:      # if current teams are not already playing and the field is free
                    teams_playing.extend(teams)
                    fields_taken.append(field)
                    games.at[row,'timeslot'] = timeslot
    return(games)


def get_gap_info(games):
    """
    Get the length of the gaps between games (for every team)

    :param games: (pd.DataFrame) list of games
    :return: (np.array) gaps between games. rows are teams
    """
    teams = sorted(np.unique(games[['home', 'away']].values))
    maxschedule = max(games.timeslot)
    gaps = []
    for team in teams:
        schedule = sorted(games[(games.home==team) | (games.away==team)].timeslot)
        schedule_gaps = [z-1 for z in np.diff([0]+schedule+[maxschedule+1])]
        gaps.append(schedule_gaps)
    return(gaps)


def get_criteria(games):
    """
    Returns the criteria used for schedule selection
    # 1. Overall maximum gap between any two games of the same team
    # 2. Overall maximum total gap before+after a game (gaps with game in-between)
    # 3. Average (over teams) maximum gap between any two games
    # 4. Average (over teams) maximum gap before+after a game (gaps with game in-between)

    :param games: (pd.DataFrame) list of games with time slots
    :return: (tuple)
    """
    gapinfo = get_gap_info(games)
    consecgaps = [[z[i]+z[i+1] for i in range(len(z)-1)] for z in gapinfo]
    crit1 = max([max(z) for z in gapinfo])     # max gap
    crit2 = max([max(z) for z in consecgaps])  # max gap with game in-between
    crit3 = np.mean([max(z) for z in gapinfo])
    crit4 = np.mean([max(z) for z in consecgaps])
    return(crit1,crit2,crit3,crit4)


def get_best_schedule(teams, nfield=3, nbest=0, patience=200):
    """
    Tries random schedules and returns only the best one, according to the ordered criteria returned by function get_criteria

    :param teams: (list) team names
    :param nfield: (int) total number of fields
    :param nbest: (int) number of better fields
    :param patience: (int) determines how many different schedules to try
    """

    if (patience<1):
        raise ValueError('patience entry has to be a positive integer')
    games, perfect_matches, okay = gg.get_best_match(teams, nfield, nbest)
    while perfect_matches<nbest or okay==0:
        print('No satisfactory solution with',nfield,'fields,',len(teams),'teams and',nbest,'perfect matches.')
        nfield -= 1
        if nbest > nfield: nbest -=1
        games, perfect_matches, okay = gg.get_best_match(teams, nfield, nbest)
    nfield = len(np.unique(games.field))
    print('Found a satisfactory solution with',nfield,'fields and', min(nfield,perfect_matches), 'perfect matches')

    best1, best2, best3 = 1e5, 1e5, 1e5
    noprogress=0
    while noprogress<patience:
        schedule = get_schedule(games)
        crit1, crit2, crit3, crit4 = get_criteria(schedule) # choose whichever order of criteria
        if crit1 < best1:
            best_sched = schedule
            best1 = crit1
            best2 = crit2
            best3 = crit3
        elif crit1==best1 and crit2<best2:
            best_sched = schedule
            best2 = crit2
            best3 = crit3
        elif crit1==best1 and crit2==best2 and crit3<best3:
            best_sched = schedule
            best3 = crit3
        else: noprogress+=1
    print('The schedule requires', int(max(best_sched.timeslot)), 'time slots')
    return(best_sched)


def pivot_schedule(games):
    """
    Pivot the schedule and reorder the columns

    :param games: (pd.DataFrame) list of games with time slots (output of get_schedule or get_best_schedule)
    :return: (pd.DataFrame) pivoted schedule, easier to read
    """
    schedule = games.pivot(index='timeslot', columns='field')
    schedule.columns = schedule.columns.set_names(['home_away', 'field'])
    schedule = schedule.swaplevel(1,0,1)
    newcols = schedule.columns.tolist()
    newcols = sorted(newcols, key=lambda z: (-z[0],z[1]), reverse=True)
    return(schedule[newcols])
