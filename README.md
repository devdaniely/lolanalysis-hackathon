"# lolanalysis-hackathon" 


### Notes:
- Tech Doc: https://docs.google.com/document/d/1wFRehKMJkkRR5zyjEZyaVL9H3ZbhP7_wP0FBE5ID40c/edit
- AWS Athena Data doc: https://docs.google.com/document/d/14uhbMUYb7cR_Hg6UWjlAgnN-hSy0ymhz19-_A6eidxI/edit?pli=1


### Research:
- Calculating ELO: https://leagueoflegends.fandom.com/wiki/Elo_rating_system#Calculating_Elo
- FIFA: https://digitalhub.fifa.com/m/f99da4f73212220/original/edbm045h0udbwkqew35a-pdf.pdf
- NCAA Basketball Ranking Formula: https://towardsdatascience.com/college-basketballs-net-rankings-explained-25faa0ce71ed


#### Code References: 
- https://github.com/kylekap/Sports_Ranking_Systems

#### External Data:
- https://oracleselixir.com/stats/teams/byTournament

--------------

# TODO

1. Connect python script to S3 bucket
2. EC2 run calculations and place in csv into S3
3. Combine calculation files and end game data
4. Run ML on data to find feature weights
5. Put into ELO formula
6. Write lambda to calculate ELO based on teams
7. Connect with API gateway


--------------


**/esports-data** - contains overview info
**/games** - contains minute data. Created with downloaddata.py

- `downloaddata.py` will download .gz files into the /games folder

- `analyze.py` is current playground file

--------------
# Formula
- TODO: Modify ELO rating with new variables from ML
- Factor in sequencing/proximity coefficients

## ELO
Rating (new) = Rating (old) + K * (GameResult - Expected)

Expected = 1 / (1 + 10 ^ ([TeamBRating - TeamARating] / 400) )

K = efficiency differential

## KenPom (Basketball predictive)
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


Modified WinPredict ratio = 
```
       actualgoldSpent^x 
--------------------------------
actualgoldSpent^x + sumtotalgold^x
```

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

If we use proximity as the K value
```
| win | proximity_sum | normalized (over 6 five min periods) |
|-----|---------------|--------------------------------------|
| 1   | 17.14955      | 2.8582583333333333                   |
| 0   | 13.10038      | 2.1833966666666666                   |
|     |               |                                      |
```

- TL = 1200 + (15 + 2.8582583333333333) * (1 - 0.08189800214) = 1216.39570265
- DIG = 1200 + (15 + 2.1833966666666666) * (0 - 0.05322815987) = 1199.08535942


## Glicko Rating
https://en.wikipedia.org/wiki/Glicko_rating_system


-------------------

#### Sequencing
1. Split game df into 5min intervals
2. Map eventType into sequences at the team level
  - Ex: ward_placed = "A", ocean_drag = "B", etc.
  - Output = win_seq_1-5 = "AABC", win_seq_5-10 = "CCDDE", lose_seq_1-5 = "ABCD"


#### Proximity
- https://lolesports.com/article/dev-diary-changes-to-proximity/bltc57ec217dbf2a162
  - 2000 units

1. Split game df into 5min intervals
2. ProximityArea = Area of Circle with radius 1000
3. Using position data of 5 players, count # of triangles with area < ProximityArea
  - Output = win_prox_1-5 = 3, win_prox_5-10 = 2
