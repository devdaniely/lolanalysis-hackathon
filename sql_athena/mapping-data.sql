CREATE EXTERNAL TABLE lol.`mapping_data`(
  `esportsgameid` string, 
  `platformgameid` string, 
  `teammapping` struct<`200`:string,`100`:string>,
  `participantmapping` struct<`3`:string,`5`:string,`10`:string,`2`:string,`1`:string,`9`:string,`7`:string,`8`:string,`6`:string,`4`:string>)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
WITH SERDEPROPERTIES ( 
  'paths'='esportsGameId,participantMapping,platformGameId,teamMapping') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://power-rankings-dataset-gprhack/athena-ready/mapping-data'
TBLPROPERTIES (
  'classification'='json',
  'compressionType'='bzip2', 
  'typeOfData'='file')
