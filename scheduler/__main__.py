import sys
import click
import pandas
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import schedule_generation as sg

@click.command()
@click.option('--nfield', type=int, help='Number of available fields (must be specified)')
@click.option('--nteams', type=int, default=0, help='Number of teams (must be specified if team names are not)')
@click.option('--nbest', type=int, default=-1, help='Number of fields on which each team has to play the same amount of games (defaults to all fields)')
@click.option('--patience', type=int, default=200, help='Patience parameter for the schedule optimization')
@click.option('--out', type=str, default='schedule.csv', help='Filename for the CSV output')
@click.argument('team_names', nargs=-1)
def main(team_names, nteams, nfield, nbest, patience, out):
    """CSV export of the best tournament schedule for the specified number of teams and fields, under the constraint that every team must play the same amount of games on some fields.
    """
    if nbest==-1: nbest = nfield
    elif nbest>nfield: raise ValueError('--nbest cannot be higher than --nfield')
    if nfield is None: raise ValueError('Please specify a positive number of fields (--nfield option)')
    if nbest<0: raise ValueError('Please specify a positive number of fields (--nfield option)')
    if nteams>0 and len(team_names)>0 : print("Parameter nteams ignored: team names are already specified")
    elif nteams==0 and len(team_names)==0: raise ValueError('Please specify a positive number of teams (--nteams option)')
    
    if len(team_names)>0: nteams = len(team_names)
    else: team_names = ['Team ' + str(z+1) for z in range(nteams)]

    games = sg.get_best_schedule(list(team_names), nfield, nbest, patience)
    schedule = sg.pivot_schedule(games)
    schedule.to_csv(out)
    print('Output saved to', os.getcwd() + '/' + out)

if __name__ == '__main__':
    main()
