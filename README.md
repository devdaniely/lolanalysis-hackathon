# ELO Rating with Proximity Scores

## API Examples

The lambdas will run calculations on the data as this will be easier to scale and incorporate new data in the future.

### `/global_rankings`
Returns the current rankings of all teams since the beginning of 2023

- https://mqb2k0rcn5.execute-api.us-west-2.amazonaws.com/Prod/global_rankings
- https://mqb2k0rcn5.execute-api.us-west-2.amazonaws.com/Prod/global_rankings?number_of_teams=50

### `/tournament_rankings/{tournament_id}?stage={stage_name}`
Returns the rankings of the teams in the tournament based off the prior 6 months

- API Gateway (30 sec timeout)
  - https://mqb2k0rcn5.execute-api.us-west-2.amazonaws.com/Prod/tournament_rankings/105873410870441926?stage=round_1
- Lambda Invoke (5 min timeout)
  - https://hpbgvizwe3dxaiydlvjh5y3xli0vymmz.lambda-url.us-west-2.on.aws/tournament_rankings/105873410870441926?stage=round_1

### `/team_rankings?team_ids={team_ids_array}`
Returns the rankings for each team dating back to 2020
- API Gateway
  - https://mqb2k0rcn5.execute-api.us-west-2.amazonaws.com/Prod/team_rankings?team_ids=98926509885559666&team_ids=98767991877340524
- Lambda Invoke
  - https://cg25zzqwk2unw5xq3c67riazz40ztpmt.lambda-url.us-west-2.on.aws/team_rankings?team_ids=98926509885559666,98767991877340524,98767991892579754,98767991853197861



# Research:
- Tech Doc: https://docs.google.com/document/d/1wFRehKMJkkRR5zyjEZyaVL9H3ZbhP7_wP0FBE5ID40c/edit
- AWS Athena Data doc: https://docs.google.com/document/d/14uhbMUYb7cR_Hg6UWjlAgnN-hSy0ymhz19-_A6eidxI/edit?pli=1

## Calculations
- Calculating ELO: https://leagueoflegends.fandom.com/wiki/Elo_rating_system#Calculating_Elo
- Getting Proximity: https://lolesports.com/article/dev-diary-changes-to-proximity/bltc57ec217dbf2a162
  - https://www.doranslab.gg/articles/location-based-champ-metrics.html
- NCAA Basketball Ranking Formula: https://towardsdatascience.com/college-basketballs-net-rankings-explained-25faa0ce71ed
- KenPom Basketball: https://kenpom.com/blog/ratings-explanation/
- FIFA: https://digitalhub.fifa.com/m/f99da4f73212220/original/edbm045h0udbwkqew35a-pdf.pdf


## External Data:
- https://oracleselixir.com/stats/teams/byTournament


--------------

**/esports-data** - contains overview info
**/games** - contains minute data. Created with downloaddata.py

- `downloaddata.py` will download .gz files into the /games folder

- `analyze.py` is current playground file

--------------
# Formula
Example is at the bottom of this README

Rating (new) = Rating (old) + K * (GameResult - (Expected + DiffWinPredictRatio))

Expected = 1 / (1 + 10 ^ ([ProxSumA - ProxSumB] / 400) )

DiffWinPredictRatio = Difference in Pythagorean Expectation of each team in gold 
```
       actualgoldSpent^x 
--------------------------------
actualgoldSpent^x + sumtotalgold^x

```


## Research

### ELO
Rating (new) = Rating (old) + K * (GameResult - Expected)

Expected = 1 / (1 + 10 ^ ([TeamBRating - TeamARating] / 400) )

K = efficiency differential

### KenPom (Basketball predictive)
Pythagorean Expectation
- https://en.wikipedia.org/wiki/Pythagorean_expectation


Example: ESPORTSTMNT01_3311408 (TL win, DIG lose)
```
| win | totalgold | earnedgold | goldspent |
|-----|-----------|------------|-----------|
| 1   | 50211     | 34043      | 42818     |
| 0   | 39018     | 22850      | 37235     |
|     |           |            |           |
```

Passive gold = totalgold - earnedgold
Actual Gold Spent = goldspent - (passive gold)
```
| win | totalgold | earnedgold | goldspent | actualGoldSpent |
|-----|-----------|------------|-----------|-----------------|
| 1   | 50211     | 34043      | 42818     | 26650           |
| 0   | 39018     | 22850      | 37235     | 21157           |
|     |           |            |           |                 |
```


### WinPredict ratio = 
```
       actualgoldSpent^x 
--------------------------------
actualgoldSpent^x + sumtotalgold^x
```
x = 1.83 

Exponent value 1.83 taken from baseball: https://en.wikipedia.org/wiki/Pythagorean_expectation


- TL = 26650^2 / (26650^2 + 89229^2) = 0.08189800214
- DIG = 21157^2 / (21157^2 + 89229^2) = 0.05322815987


Plugging this into the ELO formula with initial 1200 and K=15
```
New Rating A = Old Rating A + K * (Result A - Expected Outcome A)
New Rating B = Old Rating B + K * (Result B - Expected Outcome B)
```

- TL = 1200 + 15 * (1 - 0.08189800214) = 1213.77152997
- DIG = 1200 + 15 * (0 - 0.05322815987) = 1199.2015776

#### Including Proximity in the formula

Proximity data
```
| win | proximity_sum |
|-----|---------------|
| 1   | 17.14955      |
| 0   | 13.10038      | 
|     |               | 
```

### Glicko Rating
https://en.wikipedia.org/wiki/Glicko_rating_system


## Example using the data from above

Rating (new) = Rating (old) + K * (GameResult - (Expected + DiffWinPredictRatio))

K = 15 (based on https://leagueoflegends.fandom.com/wiki/Elo_rating_system)

Expected = 1 / (1 + 10 ^ ([ProxSumA - ProxSumB] / 400) )

DiffWinPredictRatio = Difference in Pythagorean Expectation of each team in gold 

--------

Expect = 1 / (1 + 10 ^ ((17.141955 - 13.10038) / 400)) = **0.49418396836**

DiffWinPredictRatio = 0.09873115791991857 - 0.06650851712236172 = **0.03222264079**
- TL = 26650^1.83  / (26650^1.83 + 89229^1.83) = 0.09873115791991857
- DIG = 21157^1.83 / (21157^1.83 + 89229^1.83) = 0.06650851712236172

Rating: 1200 + 15 * (1 - (0.49418396836 + 0.03222264079))

- **TL = 1207.10390086**
- **DIG = 1192.10390086**

Proximity scores are running averages:
- TeamA_game1 proximity_sum = 10
- TeamA_game1 proximity_score = 10
- TeamA_game2 proximity_sum = 6
- **TeamA_game2 proximity_score = 8**

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




























