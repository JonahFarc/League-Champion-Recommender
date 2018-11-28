import time
import requests
import json
import datetime

#Hardcoded URL variables
url_base = "https://na1.api.riotgames.com/lol/"
url_mastery = "champion-mastery/v3/champion-masteries/by-summoner/"
url_version = "https://ddragon.leagueoflegends.com/realms/na.json"
API_KEYS = ["Removed"]
API_KEY_INDEX = 0

#Create a champion map to map the champion's id number to their name
champ_version = json.loads(requests.get(url_version).content)["n"]["champion"]
champ_map = {}
champ_response = requests.get("http://ddragon.leagueoflegends.com/cdn/" + champ_version + "/data/en_US/champion.json")
champ_json = json.loads(champ_response.content)
for champ in champ_json["data"].keys():
    champ_map[champ_json["data"][champ]["key"]] = champ_json["data"][champ]["name"]

#open files to read and write
readfile = open("roster2.csv", "r")
file = open("rosterFIXED.csv", "w", 1)
file.write(
    "Summoner Name,Summoner Id,Summoner Level,Champion Name,Champion Id,Mastery Points,Mastery Level,Last Played Acc Date,Last Played Champ Date\n")

#Create var to skip certain lines
count_skip = 2
for line in readfile:
    print(line)
    if count_skip > 0:
        count_skip = (count_skip + 1) % 3
        continue

    #split and pull constant data
    data = line.split(',')
    summonername = data[0]
    summonerid = data[1]
    summonerlevel = data[2]
    accdate = data[7]

    #pull champion mastery from API for the summoner
    mast_url = url_base + url_mastery + str(summonerid) + "?api_key=" + API_KEYS[API_KEY_INDEX]
    API_KEY_INDEX = (API_KEY_INDEX + 1) % len(API_KEYS)
    mast_response = requests.get(mast_url)
    # print("Mastery response code: " + str(mastresponse.status_code))
    mast_json = json.loads(mast_response.content)
    print("Summoner: " + summonername)
    print("Mastery Json: " + str(mast_json))

    #pull mastery for all champs
    for x in range(0, len(mast_json)):
        text = "{SummonerName},{SummonerId},{SummonerLevel},{ChampionName},{ChampionId},{MasteryPoints},{MasteryLevel},{LastPlayedAcc},{LastPlayedChamp}".format(
            SummonerName=summonername,
            SummonerId=summonerid,
            SummonerLevel=summonerlevel,
            ChampionName=champ_map[str(mast_json[x]["championId"])],
            ChampionId=mast_json[x]["championId"],
            MasteryPoints=mast_json[x]["championPoints"],
            MasteryLevel=mast_json[x]["championLevel"],
            LastPlayedAcc=accdate,
            LastPlayedChamp=str(datetime.datetime.fromtimestamp(
                mast_json[x]["lastPlayTime"] / 1000).strftime('%Y-%m-%d %H:%M:%S')))
        file.write(text + "\n")
        #print(text)
    count_skip = count_skip + 1
    time.sleep(0.15)
