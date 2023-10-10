CREATE EXTERNAL TABLE lol.`players`(
  `player_id` string, 
  `handle` string, 
  `first_name` string, 
  `last_name` string, 
  `home_team_id` string)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
WITH SERDEPROPERTIES ( 
  'paths'='first_name,handle,home_team_id,last_name,player_id') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://power-rankings-dataset-gprhack/athena-ready/players'
TBLPROPERTIES (
  'classification'='json',
  'compressionType'='bzip2', 
  'typeOfData'='file')