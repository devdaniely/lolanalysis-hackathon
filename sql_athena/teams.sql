CREATE EXTERNAL TABLE lol.`teams`(
  `team_id` string, 
  `name` string, 
  `acronym` string, 
  `slug` string)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
WITH SERDEPROPERTIES ( 
  'paths'='acronym,name,slug,team_id') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://power-rankings-dataset-gprhack/athena-ready/teams'
TBLPROPERTIES (
  'classification'='json',
  'compressionType'='bzip2', 
  'typeOfData'='file')