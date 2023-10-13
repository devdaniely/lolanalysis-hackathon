import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
import pandas as pd 
import numpy as np
from skspatial.measurement import area_signed

filepath = "./games/lck_spring_2023/"
filename = "ESPORTSTMNT01_3303961.gz"
filegz = filepath + filename

output_file = "test_output.xlsx"


def analyze():

    df = pd.read_json(filegz, compression="gzip")
    #print(df[:100])

    df = df[df["eventType"] == "champion_kill"]

    for idx, row in df.iterrows():
        print(row)
        input()


    # Write out file
    #df.to_excel(output_file)

    part_df = df["participants"]



def calculateArea(part_df):
    # Split participants into teams
    blue_players_filter = filter(lambda x: x["teamID"] == 100, part_df_row)
    blue_players = list(blue_players_filter)
    blue_positions_map = map(lambda p: (p["position"]["x"], p["position"]["z"]), blue_players)
    blue_positions = list(blue_positions_map)

    # Calculate area
    area = area_signed(sort_counterclockwise(blue_positions))


    





# https://stackoverflow.com/questions/69100978/how-to-sort-a-list-of-points-in-clockwise-anti-clockwise-in-python
def sort_counterclockwise(points, centre = None):
  if centre:
    centre_x, centre_y = centre
  else:
    centre_x, centre_y = sum([x for x,_ in points])/len(points), sum([y for _,y in points])/len(points)
  angles = [math.atan2(y - centre_y, x - centre_x) for x,y in points]
  counterclockwise_indices = sorted(range(len(points)), key=lambda i: angles[i])
  counterclockwise_points = [points[i] for i in counterclockwise_indices]
  return counterclockwise_points














if __name__ == "__main__":
   #analyze()
   df = pd.read_json("./esports-data/tournaments.json")
   df.to_excel("test_tournament_output.xlsx")
