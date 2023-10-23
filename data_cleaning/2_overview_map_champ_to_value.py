
import os
import pandas as pd 

filepath = "./data/overviews/"

# Create champion map
champ_df = pd.read_csv("./data/champions.csv")
# Convert to dict
champ_dict = dict(zip(champ_df.Champion, champ_df.ChampIndex))


for file in os.listdir(filepath):

    print("Processing: {}".format(file))

    curFile = filepath + file
    df = pd.read_csv(curFile, low_memory=False)

    df.replace({"champ1": champ_dict}, inplace=True)
    df.replace({"champ2": champ_dict}, inplace=True)
    df.replace({"champ3": champ_dict}, inplace=True)
    df.replace({"champ4": champ_dict}, inplace=True)
    df.replace({"champ5": champ_dict}, inplace=True)

    df.replace({"ban1": champ_dict}, inplace=True)
    df.replace({"ban2": champ_dict}, inplace=True)
    df.replace({"ban3": champ_dict}, inplace=True)
    df.replace({"ban4": champ_dict}, inplace=True)
    df.replace({"ban5": champ_dict}, inplace=True)

    output_file = "champMapped_" + file
    df.to_csv(output_file, index=False)







