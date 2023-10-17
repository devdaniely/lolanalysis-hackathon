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
