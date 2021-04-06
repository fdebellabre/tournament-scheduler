import random
import itertools as it
import pandas as pd
import numpy as np


def games_on_field(df, game_id, field):
    """
    :param df: (pd.DataFrame) list of games
    :param game_id: (int) identifier of the game at stake
    :param field: (int) identifier of the field at stake
    :return: (int tuple) number of games already planned on the field by the two teams
    """
    if (field<0):
        raise ValueError('field entry has to be a non-negative integer')
    home = df.home[game_id]
    away = df.away[game_id]
    home_count = df.loc[((df.home==home) | (df.away==home))].loc[df.field==field].shape[0]
    away_count = df.loc[((df.home==away) | (df.away==away))].loc[df.field==field].shape[0]
    return(home_count, away_count)


def randomize_home_away(games):
    """
    Randomizes whether a team is displayed as playing home or away (it doesn't matter to us)

    :param games: (pd.DataFrame) list of games
    :return: (pd.DataFrame) list of games
    """
    # DataFrame games: with columns (home, away)
    unif = np.random.uniform(size=games.shape[0])
    newhome = np.where(unif>0.5, games.home, games.away)
    newaway = np.where(unif>0.5, games.away, games.home)
    games.home = newhome
    games.away = newaway
    return(games)


def get_game_list(teams, nfield, nbest):
    """
    Get a list of games with fields, from a list of teams

    :param teams: (list) team names
    :param nfield: (int) total number of fields
    :param nbest: (int) number of fields on which each team has to play an equal amount of games
    :return: (pd.DataFrame,bool) list of games and boolean to identify whether the list is complete
    """
    if (nfield<nbest):
        raise ValueError('nfield entry cannot be lower than nbest entry')
    random.shuffle(teams)
    games = pd.DataFrame(it.combinations(teams, 2))         # all combinations of 2 teams
    games = games.sample(frac=1).reset_index(drop=True)     # shuffle rows
    games.columns = ['home', 'away']
    games = randomize_home_away(games)
    games['field'] = np.nan
    ngames = games.shape[0]
    nteams = len(teams)
    # Quota to play on the best fields is the average number of games per field, times 2, divided by number of teams.
    quota = (ngames/nfield)*2/nteams
    # Go through each field and each game
    for field in range(nfield):
        for pen in (1, 0):
            for row in range(ngames):
                home_count, away_count = games_on_field(games, row, field)
                # If the teams have not played more than their quota (minus a penalization) on the current field, assign the current field to that game.
                if ((home_count < quota-pen) & (away_count < quota-pen) & np.isnan(games.field[row])):
                    games.at[row, 'field'] = field

    ## If there are games unmatched with a field, we allow teams to play more games on a given field, as long as it is not on the best fields
    for field in range(nbest,nfield):
        for row in range(ngames):
            home_count, away_count = games_on_field(games, row, field)
            if ((home_count <= quota+1) & (away_count <= quota+1) & np.isnan(games.field[row])):
                games.at[row, 'field'] = field

    if np.sum(np.isnan(games.field))>0:
        complete=False
    else:
        complete=True

    return(games,complete)


def check_list_quality(games, nfield, verbose=False):
    """
    Check the quality of the list of games.

    A field has a perfect match when each team plays the same amount of games on it.
    :param games: (pd.DataFrame) with the list of games (output of get_game_list)
    :param nfield: (int) total number of fields
    :return: (int tuple) binary tuple of length nfield, saying for each field whether every team plays the same amount of games on it
    """
    dfhome = games[['home','field']]
    dfaway = games[['away','field']]
    dfaway.columns=['home','field']
    dfboth = dfhome.append(dfaway).reset_index()
    dfboth = dfboth[np.isnan(dfboth.field)==False].groupby(['home','field']).count().reset_index()
    allcomb = pd.DataFrame(it.product(dfboth.home.unique(), range(nfield)), columns=['home', 'field'])
    dfagg = allcomb.merge(dfboth, how='left', on=['home', 'field'])
    dfagg.columns = ['team', 'field', 'gamecount']
    dfagg.gamecount = np.where(np.isnan(dfagg.gamecount), 0, dfagg.gamecount)
    perfect=[]
    for i in range(nfield):
        if min(dfagg[dfagg.field==i]['gamecount'])==max(dfagg[dfagg.field==i]['gamecount']):
            if verbose: print("Perfect match for field",i)
            perfect.append(1)
        else:
            if verbose: print("Imperfect match field",i,": min is", min(dfagg['gamecount']), "games and max is", max(dfagg['gamecount']), "games")
            perfect.append(0)
    return(perfect)


def get_best_match(teams, nfield, nbest, maxiter=20, verbose=False):
    """
    Iterate to try and find the best possible match between games and fields.
    Ideally, every team plays as much on each field.

    :param teams: (list) team names
    :param nfield: (int) total number of fields
    :param nbest: (int) number of better fields
    :param maxiter: (int) number of tries
    :param verbose: (bool)
    """
    best_perfect = 0
    for i in range(maxiter):
        games, okay = get_game_list(teams, nfield, nbest)
        if okay:
            perfect_matches = np.sum(check_list_quality(games, nfield))
            if perfect_matches==nfield:
                if verbose: print('Found a perfect match! At iteration',i)
                return(games,perfect_matches,1)
            elif best_perfect <= perfect_matches:
                best_perfect = perfect_matches
                best_games = games
    if verbose: print("No perfect match.")
    if 'best_games' in locals() or 'best_games' in globals():
        return(best_games, best_perfect, 1)
    else: return(games, best_perfect, 0)
