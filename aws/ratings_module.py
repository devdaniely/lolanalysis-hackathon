import pandas as pd
import json
from datetime import datetime, timedelta
import gzip

########################## VARIABLES START ##########################
with gzip.open("data/tournaments.json.gz", "r") as gz_file:
  tournaments_json = json.load(gz_file)
with open("data/mapping_data.json", "r") as json_file:
  mappings_data = json.load(json_file)
with open("data/teams.json", "r") as json_file:
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

overview_data = pd.read_csv("data/all_data.csv", low_memory=False)
BLUE_SIDE = "100"
RED_SIDE = "200"
BLUE_SIDE_INT = 100
RED_SIDE_INT = 200

########################## VARIABLES END ##########################

########################## RATINGS FUNCTIONS START ##########################


# Returns a dict of team -> team rating, rank
def get_ratings(initial_team_ids, esports_game_ids):
  total_teams = len(initial_team_ids)

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
    game_df = game_df.drop_duplicates()

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


# Creates initial team rating values
def create_team_dict_entry(elo=1200, message=""):
  return {
    "elo": elo,
    "prox_score": 0,
    "prox_sum": 0,
    "games_played": 0,
    "message": message
  }

########################## RATINGS FUNCTIONS END ##########################


########################## UTIL FUNCTIONS START ##########################
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
    if team_id in team_mappings.keys():
      team_data["team_id"] = team_id
      team_data["team_code"] = team_mappings[team_id]["acronym"]
      team_data["team_name"] = team_mappings[team_id]["name"]
      team_data["rank"] = rank
      rank += 1
      new_key = team_mappings[team_id]["name"]
      new_dict[new_key] = team_data
    else:
      new_dict[team_id] = team_data

  return new_dict


# Get tournament team ids
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


# Gets the ratings for all teams with games 6 months prior
def get_ratings_6months_prior(tournaments_data, team_ids):
  # Get games from 6months prior
  tournament_startDate = tournaments_data["startDate"]
  data_end = datetime.strptime(tournament_startDate, "%Y-%m-%d")
  data_start = data_end - timedelta(days=180)

  # Convert to date format
  overview_data['date'] = pd.to_datetime(overview_data['date'], format="mixed")
  
  # greater than the start date and smaller than the end date
  mask = (overview_data['date'] >= data_start) & (overview_data['date'] < data_end)
  #trim_data = overview_data[(overview_data['date'] >= data_start) & (overview_data['date'] < data_end)]
  trim_overview_data = overview_data.loc[mask]

  team_dict = dict()

  # for each team id, get the games they played
  for team_id in team_ids:
    team_id_int = int(team_id)
    team_games_df = trim_overview_data[trim_overview_data["teamid"] == team_id_int]

    # If team has no data, put elo of -1
    if team_games_df.empty:
      team_dict[team_id] = create_team_dict_entry(-1, "No games in prior 6 months")
      continue


    team_esports_gameids = map(lambda game_id: platformGameIdMappings[game_id.replace("_", ":")]["esportsGameId"], team_games_df["gameid"])
    team_rating_dict = get_ratings([team_id], team_esports_gameids)
    team_dict[team_id] = team_rating_dict[team_id]

  return team_dict

########################## UTIL FUNCTIONS END ##########################















def handler_tournament_stage(tournament_id, stage):
  tournaments_data = list(filter(lambda x: x["id"] == tournament_id, tournaments_json))

  if len(tournaments_data) != 1:
    print(f"Tournament not found! | id: {tournament_id}")
    return {
      "message": f"Tournament not found! | id: {tournament_id}"
    }
  else:
    tournaments_data = tournaments_data[0]


  team_ids = get_tournament_team_ids(tournaments_data, stage)

  team_ratings_dict = get_ratings_6months_prior(tournaments_data, team_ids)

  result = add_team_metadata(team_ratings_dict)


  return result





def handler_team_rankings(team_ids):
  '''
  Returns a list of rankings for each team in the provided
  list of team ids.

  Sample Output:
    [
      {
          "team_id": "109631326144414089",
          "team_code": "19",
          "team_name": "19 Esports",
          "rank": 1250.410386439273
      },
      {
          "team_id": "109631541326560210",
          "team_code": "RVN",
          "team_name": "Reven Esports",
          "rank": 1099.5943032910154
      }
    ]
  '''
  #print(f"[INFO] handler_team_rankings - Calculating rankings for teams: {team_ids}")

  # Copy all game data and convert teamid column to strings
  all_data = overview_data
  all_data['teamid'] = all_data['teamid'].astype(str) 
  
  # Get list of games that each team participated in
  platform_games_df = all_data[all_data['teamid'].isin(team_ids)]
  if platform_games_df.shape[0] == 0:
    print(f"[WARNING] handler_team_rankings - Could not find any games for teams {team_ids}.")
    return {
      "message": f"Could not find any games for teams {team_ids}"
    }
  
  # Get list of platform game ids
  platform_game_ids = platform_games_df['gameid'].str.replace('_', ':')

  # Covert platform game ids to esl game ids
  esl_game_ids = get_esl_games_from_platform_ids(platform_game_ids)
  

  # Rank the teams based on their performance in the list of esl games  
  team_ratings_dict = get_ratings(team_ids, esl_game_ids)
  
  ratings_dict = {}
  for team_id in team_ids:
    if team_id in team_ratings_dict:
      ratings_dict[team_id] = team_ratings_dict[team_id]
    else:
      ratings_dict[team_id] = create_team_dict_entry(-1, f"Could not find team with id: {team_id}")

  return add_team_metadata(ratings_dict)




def get_esl_games_from_platform_ids(platform_game_ids):
  '''
  Maps each platform game id to an ESL game ID and returns the
  result as a list.
  '''

  esl_game_ids = []
  for platform_game_id in platform_game_ids:

    if platform_game_id not in platformGameIdMappings:
      #print(f"[WARNING] get_esl_games_from_platform_ids - Could not find platform game id {platform_game_id} in platformGameIdMappings.\n")
      continue

    platform_game_id_mapping = platformGameIdMappings[platform_game_id]
    esl_game_ids.append(platform_game_id_mapping['esportsGameId'])

  return esl_game_ids

























#if __name__ == "__main__":
#get_games_tournament_stage("105873410870441926", "round_1")
#get_games_tournament_stage("105873410870441926", None)

# MSI 2021
#ratings = handler_tournament_stage("105873410870441926", "round_1")
#print(ratings)

# Team liquid vs digitas example
#get_ratings(["98926509885559666", "98926509883054987"], ["109517090067719793"])
#print(overview_data.head())