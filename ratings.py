import pandas as pd
import json
from datetime import datetime, timedelta


# Init variables
with open("esports-data/tournaments.json", "r") as json_file:
  tournaments_json = json.load(json_file)
with open("esports-data/mapping_data.json", "r") as json_file:
  mappings_data = json.load(json_file)
with open("esports-data/teams.json", "r") as json_file:
  teams_data = json.load(json_file)

# Key is 109517090067719793
esportsGameIdMappings = {
  esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
}

# Key is ESPORTSTMNT01:3311408
platformGameIdMappings = {
  platform_game["platformGameId"]: platform_game for platform_game in mappings_data
}

team_mappings = {
  team_data["team_id"]: team_data for team_data in teams_data
}


overview_data = pd.read_csv("./data/all_data.csv", engine="pyarrow")
BLUE_SIDE = "100"
RED_SIDE = "200"
BLUE_SIDE_INT = 100
RED_SIDE_INT = 200





# Returns a long number
def get_tournament_game_ids(tournaments_data, stage):
  # List of all games  in stage
  game_ids = []

  # Get all stages
  if stage is not None:
    stage_data_list = filter(lambda x: x["slug"] == stage or x["name"] == stage, tournaments_data["stages"])
  else:
    stage_data_list = tournaments_data["stages"]

  # Get all teams in stage_data_list
  for stage_data in stage_data_list:
    sections_list = stage_data["sections"]

    for section in sections_list:
      match_games = map(lambda match: match["games"], section["matches"])

      for games_list in match_games:
        game_ids += list(map(lambda game: game["id"], games_list))
    
  return game_ids


# Get tournament teams
def get_tournament_team_ids(tournaments_data, stage):
  team_ids = []

  # Get all stages
  if stage is not None:
    stage_data_list = filter(lambda x: x["slug"] == stage or x["name"] == stage, tournaments_data["stages"])
  else:
    stage_data_list = tournaments_data["stages"]

  # Get all teams in stage_data_list
  for stage_data in stage_data_list:
    sections_list = stage_data["sections"]

    for section in sections_list:
      match_teams = map(lambda match: match["teams"], section["matches"])

      for teams_list in match_teams:
        team_ids += list(map(lambda team: team["id"], teams_list))
    
  return set(team_ids)


# game_ids are tournament gameids
def get_team_ids_from_games(game_ids):

  teams = []

  for game_id in game_ids:
    if game_id in esportsGameIdMappings.keys():
      team1 = esportsGameIdMappings[game_id]["teamMapping"]["100"]
      team2 = esportsGameIdMappings[game_id]["teamMapping"]["200"]
      if team1 not in teams:
        teams.append(team1)
      if team2 not in teams:
        teams.append(team2)

  return teams

# Gets team names from tournament gameids
def get_team_names_from_team_ids(team_ids):
  return list(map(lambda team_id: team_mappings[team_id], team_ids))



def get_ratings_6months_prior(tournaments_data, team_ids):
  # Get games from 6months prior
  tournament_startDate = tournaments_data["startDate"]
  data_end = datetime.strptime(tournament_startDate, "%Y-%m-%d")
  data_start = data_end - timedelta(days=180)

  # greater than the start date and smaller than the end date
  overview_data['date'] = pd.to_datetime(overview_data['date'])
  mask = (overview_data['date'] >= data_start) & (overview_data['date'] < data_end)
  trim_overview_data = overview_data.loc[mask]

  team_dict = dict()

  # for each team id, get the games they played
  for team_id in team_ids:
    team_id_int = int(team_id)
    team_games_df = trim_overview_data[trim_overview_data["teamid"] == team_id_int]

    # If team has no data, put elo of -1
    if team_games_df.empty:
      team_dict[team_id] = create_team_dict_entry(-1)
      continue


    team_esports_gameids = map(lambda game_id: platformGameIdMappings[game_id.replace("_", ":")]["esportsGameId"], team_games_df["gameid"])
    team_rating_dict = get_ratings([team_id], team_esports_gameids)
    team_dict[team_id] = team_rating_dict[team_id]

  return team_dict



def handler_tournament_stage(tournament_id, stage):
  tournaments_data = list(filter(lambda x: x["id"] == tournament_id, tournaments_json))

  if len(tournaments_data) != 1:
    print("Tournament not found! | id: {tournament_id}")
    return {}
  else:
    tournaments_data = tournaments_data[0]

  # KEEP Get all tournament_game_ids
  #tournament_game_ids = get_tournament_game_ids(tournaments_data, stage)
  team_ids = get_tournament_team_ids(tournaments_data, stage)

  team_dict = get_ratings_6months_prior(tournaments_data, team_ids)

  print(add_team_metadata(team_dict))
  exit()



  # Get teams
  #team_ids = get_team_ids_from_games(tournament_game_ids)
  #teams = get_team_names_from_team_ids(team_ids)

  # -----
  team_ids = get_tournament_team_ids(tournaments_data, stage)
  teams = get_team_names_from_team_ids(team_ids)
  print(list(map(lambda x: x["name"], teams)))

  exit()
  #print(list(map(lambda x: x["name"], teams)))
  #print(team_names)

  team_dict = get_ratings(team_ids, tournament_game_ids)
  ranked_dict = add_team_metadata(team_dict)
  print(ranked_dict)



'''
Prepare API response structure

Value looks like
{
  '98767991926151025': {
    'elo': 1183.0688425872502, 
    'prox_score': 26.561774671666665, 
    'prox_sum': 159.37064802999998, 
    'games_played': 6
  }
}
'''
def add_team_metadata(team_dict):
  new_dict = {}
  rank = 1

  # Sort by ELO descending
  sorted_dict = dict(sorted(team_dict.items(), key=lambda item: item[1]['elo'], reverse=True))

  for team_id, team_data in sorted_dict.items():
    team_data["team_id"] = team_id
    team_data["team_code"] = team_mappings[team_id]["acronym"]
    team_data["team_name"] = team_mappings[team_id]["name"]
    team_data["rank"] = rank
    rank += 1

    new_key = team_mappings[team_id]["name"]
    new_dict[new_key] = team_data

  return new_dict


#####################################################################
# Ratings code

def create_team_dict_entry(elo=1200):
  return {
    "elo": elo,
    "prox_score": 0,
    "prox_sum": 0,
    "games_played": 0
  }

'''
Returns a dict of team -> team rating, rank
'''
def get_ratings(initial_team_ids, esports_game_ids):
  total_teams = len(initial_team_ids)

  '''
  {
    team_id: {
      elo: int (starting 1200)
      prox_score: prox_sum/games_played
      prox_sum: int
      games_played: int 
    }
  }
  '''
  # init team dict
  team_dict = dict()

  for esports_game_id in esports_game_ids:

    # skip if game missing
    if esports_game_id not in esportsGameIdMappings.keys():
      continue

    game_map = esportsGameIdMappings[esports_game_id]
    game_id = game_map["platformGameId"].replace(":", "_")

    # Skip if game missing
    if game_id not in overview_data["gameid"].unique():
      continue

    game_df = overview_data[overview_data["gameid"] == game_id]

    # Teams for game
    teamA_id = game_map['teamMapping'][BLUE_SIDE]
    teamB_id = game_map['teamMapping'][RED_SIDE]
    if teamA_id not in team_dict.keys():
      team_dict[teamA_id] = create_team_dict_entry()
    if teamB_id not in team_dict.keys():
      team_dict[teamB_id] = create_team_dict_entry()


    # Get data for calculations
    teamA_df = game_df[game_df["participantid"] == BLUE_SIDE_INT]
    teamB_df = game_df[game_df["participantid"] == RED_SIDE_INT]

    win_diff_ratio = get_win_predict_diff_ratio(game_df, teamA_df, teamB_df)
    team_dict = update_team_elo(team_dict, teamA_id, teamB_id, game_df, win_diff_ratio)

  return team_dict

'''
Rating (new) = Rating (old) + K * (GameResult - (Expected + DiffWinPredictRatio))
Expected = 1 / (1 + 10 ^ ([ProxSumA - ProxSumB] / 400) )
DiffWinPredictRatio = Difference in Pythagorean Expectation of each team in gold 

ELO formula from: https://leagueoflegends.fandom.com/wiki/Elo_rating_system

Returns (teamA_elo, teamB_elo) tuple
'''
def update_team_elo(team_dict, teamA_id, teamB_id, game_df, win_diff_ratio):
  k = 15

  teamA_df = game_df[game_df["participantid"] == BLUE_SIDE_INT]
  teamB_df = game_df[game_df["participantid"] == RED_SIDE_INT]
  teamA_proxSum = teamA_df["proximity_sum"].item()
  teamB_proxSum = teamB_df["proximity_sum"].item()

  expected = 1 / (1 + 10 ** (abs(teamA_proxSum - teamB_proxSum) / 400) )
  teamA_rating = team_dict[teamA_id]["elo"] + k * (teamA_df["result"].item() - (expected + win_diff_ratio))
  teamB_rating = team_dict[teamB_id]["elo"] + k * (teamB_df["result"].item() - (expected + win_diff_ratio))

  # Update team dict
  team_dict[teamA_id]["elo"] = teamA_rating
  team_dict[teamA_id]["prox_sum"] += teamA_proxSum
  team_dict[teamA_id]["games_played"] += 1
  team_dict[teamA_id]["prox_score"] = team_dict[teamA_id]["prox_sum"] / team_dict[teamA_id]["games_played"]

  team_dict[teamB_id]["elo"] = teamB_rating
  team_dict[teamB_id]["prox_sum"] += teamB_proxSum
  team_dict[teamB_id]["games_played"] += 1
  team_dict[teamB_id]["prox_score"] = team_dict[teamB_id]["prox_sum"] / team_dict[teamB_id]["games_played"]

  return team_dict





'''
Difference in Pythagorean Expectation of each team in gold 

Win predictive ratio using Pythagorean Expectation of gold
- https://en.wikipedia.org/wiki/Pythagorean_expectation

       actualgoldSpent^x 
--------------------------------
actualgoldSpent^x + sumtotalgold^x

sumtotalgold = total gold of both teams

Returns difference in win ratios
'''
def get_win_predict_diff_ratio(game_df, teamA_df, teamB_df):
  exp = 1.83 # exponent value used in baseball
  totalGold = sum(game_df["totalgold"])

  teamA_passive_gold = (teamA_df["totalgold"] - teamA_df["earnedgold"]).item()
  teamA_actual_goldSpent = (teamA_df["goldspent"] - teamA_passive_gold).item()

  teamB_passive_gold = (teamB_df["totalgold"] - teamB_df["earnedgold"]).item()
  teamB_actual_goldSpent = (teamB_df["goldspent"] - teamB_passive_gold).item()

  teamA_ratio = (teamA_actual_goldSpent ** exp) / (teamA_actual_goldSpent ** exp + totalGold ** exp)
  teamB_ratio = (teamB_actual_goldSpent ** exp) / (teamB_actual_goldSpent ** exp + totalGold ** exp)

  return abs(teamA_ratio - teamB_ratio)
  


#####################################################################

if __name__ == "__main__":

  #get_games_tournament_stage("105873410870441926", "round_1")
  #get_games_tournament_stage("105873410870441926", None)

  # MSI 2021
  handler_tournament_stage("105873410870441926", "round_1")

  # Team liquid vs digitas example
  #get_ratings(["98926509885559666", "98926509883054987"], ["109517090067719793"])
  #print(overview_data.head())


















