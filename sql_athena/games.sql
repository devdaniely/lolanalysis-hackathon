CREATE EXTERNAL TABLE lol.`games`(
  `eventtime` string,
  `eventtype` string,
  `platformgameid` string,
  `participants` array<struct<keystoneid:bigint,hashedip:string,teamid:bigint,participantid:bigint,championname:string,accountid:bigint,abgroup:string,perks:array<struct<perkids:array<int>,perkstyle:bigint,perksubstyle:bigint>>,summonername:string,summonerlevel:bigint,magicpenetrationpercent:bigint,primaryabilityresource:bigint,cooldownreduction:bigint,spellvamp:bigint,lifesteal:bigint,magicpenetrationpercentbonus:bigint,magicpenetration:bigint,primaryabilityresourceregen:bigint,healthmax:bigint,position:struct<z:bigint,x:bigint>,magicresist:bigint,primaryabilityresourcemax:bigint,armorpenetrationpercentbonus:bigint,armorpenetrationpercent:bigint,attackdamage:bigint,ccreduction:bigint,currentgold:bigint,healthregen:bigint,attackspeed:bigint,xp:bigint,armor:bigint,level:bigint,armorpenetration:bigint,totalgold:bigint,health:bigint,abilitypower:bigint,stats:array<struct<value:float,name:string>>,goldpersecond:bigint>>,
  `sequenceindex` bigint,
  `assistants` array<int>,
  `monstertype` string,
  `killer` int,
  `inenemyjungle` boolean,
  `killerteamid` int,
  `localgold` int,
  `globalgold` int,
  `bountygold` int,
  `killtype` string,
  `stageid` int,
  `killergold` int,
  `dragontype` string,
  `gamename` string,
  `gameversion` string,
  `statsupdateinterval` bigint,
  `playbackid` bigint,
  `gametime` bigint,
  `nextdragonspawntime` bigint,
  `nextdragonname` string,
  `gameover` boolean,
  `teams` array<struct<inhibkills:bigint,towerkills:bigint,teamid:bigint,baronkills:bigint,dragonkills:bigint,assists:bigint,championskills:bigint,totalgold:bigint,deaths:bigint>>,
  `itemid` bigint,
  `participantid` bigint,
  `goldgain` bigint,
  `itemafterundo` bigint,
  `itembeforeundo` bigint,
  `skillslot` bigint,
  `participant` bigint,
  `evolved` boolean,
  `wardtype` string,
  `position` struct<z:bigint,x:bigint>,
  `placer` bigint)
ROW FORMAT SERDE
  'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'paths'='eventTime,eventType,evolved,gameName,gameOver,gameTime,gameVersion,goldGain,itemAfterUndo,itemBeforeUndo,itemID,nextDragonName,nextDragonSpawnTime,participant,participantID,participants,placer,platformGameId,playbackID,position,sequenceIndex,skillSlot,statsUpdateInterval,teams,wardType,assistants,monsterType,killer,inEnemyJungle,killerTeamID,localgold,globalgold,bountygold,killtype,stageid,killergold,dragontype')
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://power-rankings-dataset-gprhack/athena-ready/games'
TBLPROPERTIES (
  'classification'='json',
  'compressionType'='bzip2',
  'typeOfData'='file')