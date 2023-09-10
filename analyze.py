import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
import pandas as pd 

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



if __name__ == "__main__":
   analyze()

