import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
import pandas as pd
import itertools


tournament_list = [

 'tcl_summer_2021',
 'arabian_league_summer_2023',
 'lck_challengers_summer_2023',
 'lck_summer_2023',
 'emea_masters_spring_play_ins_2023',
 'lcs_amateur_circuit_summer_2022',
 'liga_portuguesa_summer_2022',
 'lcl_spring_2022',
 'ljl_academy_2022',
 'elite_series_spring_2022',
 'lco_split_1_2022',
 'liga_portuguesa_spring_2021',
 'cblol_split_1_2021',
 'lcs_summer_2020',
 'tcl_winter_2020',
 'liga_portuguesa_spring_2023',
 'tcl_summer_2022',
 'european_masters_spring_2022_main_event',
 'nlc_spring_2022',
 'lrn_closing_2023',
 'nacl_promotion_spring_2023',
 'lec_season_finals_2023',
 'pcs_summer_2023',
 'hitpoint_masters_summer_2023',
 'cblol_academy_2023_split_1',
 'nacl_spring_2023',
 'stars_league_closing_2022',
 'honor_league_opening_2022',
 'honor_division_opening_2022',
 'hitpoint_masters_spring_2021',
 'lck_spring_2021',
 'worlds_2020',
 'lec_summer_2020',
 'liga_master_opening_2023',
 'lec_winter_2023',
 'honor_league_closing_2022',
 'lfl_2022_spring',
 'lcs_academy_spring_2022',
 'lck_spring_2022',
 'nacl_qualifiers_2_spring_2023',
 'lfl_2022_summer',
 'lcs_spring_2023',
 'vdl_opening_2023',
 'prime_league_spring_2023',
 'gll_spring_2023',
 'volcano_league_closing_2022',
 'tal_winter_2022',
 'lec_summer_2021',

]

output_headers = [
    "tournament",
    "gameId",
    "team",
    "win",
    "proximity_sum",
    "prox_score_1-5",
    "prox_score_5-10",
    "prox_score_10-15",
    "prox_score_15-20",
    "prox_score_20-25",
    "prox_score_25-30",
    "prox_score_30-35",
    "prox_score_35-40",
    "prox_score_40-45",
    "prox_score_45-50",
    "prox_score_50-55",
    "prox_score_55-60",
    "prox_score_60-65",
    "prox_score_65-70",
    "prox_score_70-75",
    "prox_score_75-80",
    "prox_score_80-85",
    "prox_score_85-90",
    "prox_score_90-95",
    "prox_score_95-100",
    "prox_score_100-105",
    "prox_score_105-110",
    "prox_score_110-115",
    "prox_score_115-120"
]


# ------------------- Variables Start --------------------

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"
# https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com/games/ESPORTSTMNT03:3199178.json.gz

output_file = "proximity_calculations.csv"

if os.path.isfile(output_file):
  output_df = pd.read_csv(output_file)
else:
  output_df = pd.DataFrame(None)

# Current game df
df = None

# AREA based on radius 1000
PROXIMITY_AREA = 3141592.65359
# ------------------- Variables End --------------------


# ------------------- Calculation Functions Start --------------------

# Returns the final win/lose team in a dict {'lose': 100, 'win': 200}
def get_win_lose_team():
    global df 

    win_lose_dict = dict()
    # Get the winning team from last row
    win_team = int(df.iloc[[-1]].winningTeam.item())

    if win_team == 200:
        win_lose_dict["lose"] = 100
    else:
        win_lose_dict["lose"] = 200

    win_lose_dict["win"] = win_team
    return win_lose_dict


# Get area of the triangle
def calculate_area(point1, point2, point3):
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    area = 0.5 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    return area


# Get # of instances where team members were in close proximity
def calculate_proximity(positions):
    # Generate all combinations of 3 points
    combinations = itertools.combinations(positions, 3)

    triangle_count = 0
    for combo in combinations:
        p1, p2, p3 = combo
        # Check if the points are not collinear (non-zero area)+
        area = calculate_area(p1, p2, p3)
        if area > 0 and area <= PROXIMITY_AREA:
            triangle_count += 1
        # print(f"Points {p1}, {p2}, {p3}, Area = {area}")

    return triangle_count


# Get team xy positions
def get_team_proximities(part_df_row, team):

    team_players_filter = filter(lambda x: x["teamID"] == team, part_df_row)
    team_players = list(team_players_filter)

    # Check if position data exists
    if "position" not in team_players[0].keys():
        return 0

    team_positions_map = map(
        lambda p: (p["position"]["x"], p["position"]["z"]), team_players
    )
    team_positions = list(team_positions_map)
    return calculate_proximity(team_positions)


# Returns the proximities for the interval
# [{'win': 3.6, 'lose': 2.13125},
# {'win': 2.1133333333333333, 'lose': 1.92}]
def get_proximities(interval):
    team_prox = dict()

    team_dict = get_win_lose_team()
    win_team = team_dict["win"]
    lose_team = team_dict["lose"]

    part_df = interval["participants"].dropna().reset_index(drop=True)

    win_prox = part_df.apply(get_team_proximities, team=win_team)
    lose_prox = part_df.apply(get_team_proximities, team=lose_team)

    if len(win_prox) > 0 and len(lose_prox) > 0:
        team_prox["win"] = win_prox.sum() / len(win_prox)
        team_prox["lose"] = lose_prox.sum() / len(lose_prox)

    return team_prox


def process_gzip(gzip_bytes, platform_game_id, tournament):
    global df 
    print("  -- Processing " + platform_game_id)

    df = pd.read_json(gzip_bytes, compression="gzip")

    # Split df into 5 min intervals
    df["eventTime"] = pd.to_datetime(df["eventTime"])
    # df_intervals is array of dataframes in 5min intervals
    df_intervals = [g for n, g in df.groupby(pd.Grouper(key="eventTime", freq="5Min"))]

    prox_calc = map(get_proximities, df_intervals)
    team_prox = list(prox_calc)

    if len(team_prox) > 0:
        append_result(team_prox, platform_game_id, tournament)


# Add result to output
def append_result(team_prox, platform_game_id, tournament):
    global output_df

    team_dict = get_win_lose_team()

    # Output headers
    win_game_data = [tournament, platform_game_id, team_dict['win'], 1]
    lose_game_data = [tournament, platform_game_id, team_dict['lose'], 0]

    # Append win team
    win_list = list(map(lambda x: x["win"], team_prox))
    win_data_row = win_game_data + [sum(win_list)] + win_list
    win_data_row.extend([None] * (len(output_headers) - len(win_data_row)))
    win_series = pd.Series(win_data_row, output_headers)

    lose_list = list(map(lambda x: x["lose"], team_prox))
    lose_data_row = lose_game_data + [sum(lose_list)] + lose_list
    lose_data_row.extend([None] * (len(output_headers) - len(lose_data_row)))
    lose_series = pd.Series(lose_data_row, output_headers)

    output_df = output_df.append([win_series, lose_series], ignore_index=True)


# ------------------- Calculation Functions End --------------------


def download_process_gzip_data(directory, platform_game_id, tournament):
    file_name = f"{directory}/{platform_game_id}"

    # If file already exists locally do not re-download game
    if platform_game_id in set(output_df["gameId"]):
        print("Skipping " + file_name)
        return

    response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz", stream=True)
    # print(f"{S3_BUCKET_URL}/{file_name}.json.gz")
    if response.status_code == 200:
        try:

            gzip_bytes = BytesIO(response.content)
            process_gzip(gzip_bytes, platform_game_id, tournament)

        except Exception as e:
            print("Error:", e)
    else:
        print(f"Failed to download {file_name}")
        print(response.content)


def process_games():
    global output_df

    start_time = time.time()
    with open("../esports-data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("../esports-data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    mappings = {
        esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
    }
    game_counter = 0

    directory = "games"

    for tournament in tournaments_data:
        if tournament["slug"] not in tournament_list:
            continue

        #start_date = tournament.get("startDate", "")
        #if start_date.startswith(str(year)):
        print(f"Processing {tournament['slug']}")
        for stage in tournament["stages"]:
            for section in stage["sections"]:
                for idx, match in enumerate(section["matches"]):
                    print("-- Downloading matches: " + str(idx) + "/" + str(len(section["matches"])))
                    for game in match["games"]:
                        if game["state"] == "completed":

                            try:
                                platform_game_id = mappings[game["id"]]["platformGameId"]
                            except KeyError:
                                print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                continue

                            download_process_gzip_data(directory, platform_game_id, tournament["slug"])

                            game_counter += 1
                            if game_counter % 10 == 0:
                                output_df.to_csv(output_file, index=False)
                                print(output_df.tail())
                                print(
                                    f"+++++ Processed {game_counter} games. Writing out data, current run time: \
                                   {round((time.time() - start_time)/60, 2)} minutes"
                                )

        print(f"Finished {tournament['slug']}, writing out csv...")
        output_df.to_csv(output_file, index=False)



if __name__ == "__main__":
  
    try:
        process_games()
    except Exception as e:
        print(e)
        output_df.to_csv(output_file, index=False)


    output_df.to_csv(output_file, index=False)
