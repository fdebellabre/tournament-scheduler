A tool to generate a CSV export of the best tournament schedule for the specified number of teams and fields, under the constraint that every team must play the same amount of games on some fields (all fields by default).

Can be used either as a command-line tool or as a regular Python module.

# Installation

## Through PyPI

```bash
$ pip install tournament-scheduler
```

## Manually

```bash
$ git clone https://github.com/fdebellabre/tournament-scheduler && cd tournament-scheduler
$ pip install .
```

# Usage

## From the command line

Either specify the team names

```bash
$ scheduler --nfield 6 Paris Bordeaux Lille Lyon Marseille Nantes Toulouse
```

Or specify the number of teams

```bash
$ scheduler --nteams 7 --nfield 6
```

## From within Python

```python
import scheduler
import numpy as np
import pandas as pd

nteams = 10
nfields = 3
bestfields = 1

teams = ['Team ' + str(z+1) for z in range(nteams)]
games = scheduler.get_best_schedule(teams,nfields,bestfields)

# Field distribution quality
scheduler.get_aggregate_data(games)

# Schedule quality
np.array(scheduler.get_gap_info(games))   # gaps between games (rows are teams)

# Save the schedule to csv
schedule = scheduler.pivot_schedule(games)
schedule.to_csv('schedule.csv')
```



# Procedure

The goal of this program is to optimize a schedule for a group tournament with those characteristics:

- any two teams must meet once
- some fields may be better than others
- each team must play the same amount of games on the better fields, and on every other field if possible

In addition to those constraints, we want to minimize the overall duration of the tournament and to optimize the rest time, such that no team has to wait for too long between two games.

The original use-case for this optimization problem was a soccer tournament with 10 teams and 3 fields, one of which being better than the others.

### 1. Getting a list of games to play on each field

In our setup, all fields are not equal. Each team must play the same number of games on the better fields (and on all fields if possible). We get a **perfect match** when this happens.

To get the best possible match between games and fields, I created the python function **get_best_match**. Depending on the number of fields and teams, there cannot always be a perfect match.

Here is a summary of what this function does:

1. Try and get each team to play as much as the other teams on every field
2. If not possible, at least have the teams play the same number of games on the better fields.
3. If not possible, decrement the number of fields to play on (*e.g.* if 5 fields are available but there is no satisfactory solution, we try and get a solution with 4 fields).

### 2. Optimizing the schedule with respect to some criteria

**Criteria:** we want to minimize the rest periods between games. In order of priority, we minimize:

1. The maximum gap between any two games of the same team
2. The maximum gap before+after a game
3. The average (across teams) maximum gap between any two games of the same team

The python function **get_best_schedule** randomly tries different schedules and returns the best of them, according to criterion 1, then criterion 2, then criterion 3.
