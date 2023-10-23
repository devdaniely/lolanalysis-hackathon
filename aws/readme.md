# NOTE: For each ranking API, scripts must be in the same directory as the /data folder (not inside /data).

You'll need to copy the scripts out when deploying and zip with the /data folder when uploading to lambda.

# For global_rankings
- https://mqb2k0rcn5.execute-api.us-west-2.amazonaws.com/Prod/global_rankings
- https://mqb2k0rcn5.execute-api.us-west-2.amazonaws.com/Prod/global_rankings?number_of_teams=50



# For team_rankings, query must look like
team_ids=98926509885559666&team_ids=98767991877340524&team_ids=98767991892579754&team_ids=98767991853197861

or 

team_ids=98926509885559666,98767991877340524,98767991892579754,98767991853197861


# For tournament_rankings
Test tournament_id: 105873410870441926
Test stage: round_1