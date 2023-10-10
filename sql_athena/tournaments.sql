CREATE EXTERNAL TABLE lol.`tournaments`(
  `id` string, 
  `leagueid` string, 
  `name` string, 
  `slug` string, 
  `sport` string, 
  `startdate` string, 
  `enddate` string, 
  `stages` array<struct<name:string,type:string,slug:string,sections:array<struct<name:string,matches:array<struct<id:string,type:string,state:string,mode:string,strategy:struct<type:string,count:int>,teams:array<struct<id:string,side:string,record:struct<wins:int,losses:int,ties:int>,result:struct<outcome:string,gamewins:int>,players:array<struct<id:string,role:string>>>>,games:array<struct<id:string,state:string,number:int,teams:array<struct<id:string,side:string,result:struct<outcome:string>>>>>>>,rankings:array<struct<ordinal:int,teams:array<struct<id:string,side:string,record:struct<wins:int,losses:int,ties:int>,result:string,players:array<struct<id:string,role:string>>>>>>>>>>)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
WITH SERDEPROPERTIES ( 
  'paths'='endDate,id,leagueId,name,slug,sport,stages,startDate') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://power-rankings-dataset-gprhack/athena-ready/tournaments'
TBLPROPERTIES (
  'classification'='json',
  'compressionType'='bzip2', 
  'typeOfData'='file')