import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
import pandas as pd 

filepath = "./data/oracles/"
#filename = "2023_LoL_esports_match_data_from_OraclesElixir.csv"



for file in os.listdir(filepath):

    curFile = filepath + file

    df = pd.read_csv(curFile, low_memory=False)
    # Year_overview.csv
    output_file = str(file[:4]) + "_overview.csv"
    output_df = pd.DataFrame(None)

    problem_ids = []
    problem_df = pd.DataFrame(None)

    # Only use complete data
    df = df[df["datacompleteness"] == "complete"]
    game_ids = df["gameid"].unique()


    for idx, gameid in enumerate(game_ids):

        print("Processing: {} | {}/{} | {}".format(file, str(idx), str(len(game_ids)), str(gameid)))

        game_df = df[df["gameid"] == gameid]

        win_df = game_df[game_df["result"] == 1]
        lose_df = game_df[game_df["result"] == 0]

        win_row = win_df[win_df["position"] == "team"]
        lose_row = lose_df[lose_df["position"] == "team"]

        # Get champions played
        try:
            win_row.insert(len(win_row.columns), "champ1", win_df[win_df["position"] == "top"].champion.iloc[0], True)
            win_row.insert(len(win_row.columns), "champ2", win_df[win_df["position"] == "jng"].champion.iloc[0], True)
            win_row.insert(len(win_row.columns), "champ3", win_df[win_df["position"] == "mid"].champion.iloc[0], True)
            win_row.insert(len(win_row.columns), "champ4", win_df[win_df["position"] == "bot"].champion.iloc[0], True)
            win_row.insert(len(win_row.columns), "champ5", win_df[win_df["position"] == "sup"].champion.iloc[0], True)

            lose_row.insert(len(lose_row.columns), "champ1", lose_df[lose_df["position"] == "top"].champion.iloc[0], True)
            lose_row.insert(len(lose_row.columns), "champ2", lose_df[lose_df["position"] == "jng"].champion.iloc[0], True)
            lose_row.insert(len(lose_row.columns), "champ3", lose_df[lose_df["position"] == "mid"].champion.iloc[0], True)
            lose_row.insert(len(lose_row.columns), "champ4", lose_df[lose_df["position"] == "bot"].champion.iloc[0], True)
            lose_row.insert(len(lose_row.columns), "champ5", lose_df[lose_df["position"] == "sup"].champion.iloc[0], True)
        except Exception as e:
            print(e)
            problem_ids.append(gameid)
            problem_df = problem_df.append(game_df, ignore_index=True)

        output_df = output_df.append(win_row, ignore_index=True)
        output_df = output_df.append(lose_row, ignore_index=True)


    output_df.to_csv(output_file, index=False)

    if len(problem_ids) > 0:
        problem_df.to_csv("PROBLEM_" + output_file)



