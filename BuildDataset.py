import time
import datetime
import requests
import json

url_base = "https://na1.api.riotgames.com/lol/"
url_mastery = "champion-mastery/v3/champion-masteries/by-summoner/"
url_summ_name = "summoner/v3/summoners/by-name/"
url_feat_games = "spectator/v3/featured-games"
url_version = "https://ddragon.leagueoflegends.com/realms/na.json"
API_KEY = "REMOVED"

file = open("roster.csv", "a", 1)
file.write("Summoner Name,Summoner Id,Summoner Level,Champion Name,Champion Id,Mastery Points,Mastery Level,Last Played Acc Date,Last Played Champ Date\n")
used_summoners = []

champ_version = json.loads(requests.get(url_version).content)["n"]["champion"]
champ_map = {}
champ_response = requests.get("http://ddragon.leagueoflegends.com/cdn/" + champ_version + "/data/en_US/champion.json")
champ_json = json.loads(champ_response.content)
for champ in champ_json["data"].keys():
    champ_map[champ_json["data"][champ]["key"]] = champ_json["data"][champ]["name"]
while (True):
    try:
        specurl = url_base + url_feat_games + "?api_key=" + API_KEY
        spec_response = requests.get(specurl)
        spec_json = json.loads(spec_response.content)
        for game in spec_json["gameList"]:
            for player in game["participants"]:
                playerid = player["summonerName"]
                if playerid in used_summoners:
                    continue
                used_summoners.append(playerid)
                summ_url = url_base + url_summ_name + str(playerid) + "?api_key=" + API_KEY
                summ_response = requests.get(summ_url)
                # print("Summoner response code: " + str(summresponse.status_code))
                summ_json = json.loads(summ_response.content)
                print("Summoner Json: " + str(summ_json))
                maxInactivityTime = 31556952000  # milliseconds in One Year
                if summ_response.status_code == 200:
                    if len(summ_json) > 0:
                        if summ_json["summonerLevel"] >= 30 and (
                                int(round(time.time() * 1000)) - summ_json["revisionDate"]) < maxInactivityTime:
                            summonerid = summ_json["id"]
                            mast_url = url_base + url_mastery + str(summonerid) + "?api_key=" + API_KEY
                            mast_response = requests.get(mast_url)
                            # print("Mastery response code: " + str(mastresponse.status_code))
                            mast_json = json.loads(mast_response.content)
                            print("Mastery Json: " + str(mast_json))
                            for x in range(0, len(mast_json)):
                                if x > 2:
                                    break
                                text = "{SummonerName},{SummonerId},{SummonerLevel},{ChampionName},{ChampionId},{MasteryPoints},{MasteryLevel},{LastPlayedAcc},{LastPlayedChamp}".format(
                                    SummonerName=summ_json["name"],
                                    SummonerId=summonerid,
                                    SummonerLevel=summ_json["summonerLevel"],
                                    ChampionName=champ_map[str(mast_json[x]["championId"])],
                                    ChampionId=mast_json[x]["championId"],
                                    MasteryPoints=mast_json[x]["championPoints"],
                                    MasteryLevel=mast_json[x]["championLevel"],
                                    LastPlayedAcc=str(datetime.datetime.fromtimestamp(
                                        summ_json["revisionDate"] / 1000).strftime('%Y-%m-%d %H:%M:%S')),
                                    LastPlayedChamp=str(datetime.datetime.fromtimestamp(
                                        mast_json[x]["lastPlayTime"] / 1000).strftime('%Y-%m-%d %H:%M:%S')))
                                file.write(text + "\n")
                                print(text)
                        else:
                            if summ_json["summonerLevel"] >= 30:
                                print("Error: Summoner{name} has been inactive for too long!".format(
                                    name=summ_json["name"]))
                            else:
                                print("Error: Summoner {name} is too low leveled!".format(name=summ_json["name"]))
                    else:
                        print("Error: Empty Summoner JSON response")
                else:
                    print("Error: Status Code: " + str(summ_response.status_code))
                print("---------------------------------------------------------")
                time.sleep(5)
            time.sleep(10)
        time.sleep(5)
        print("Refreshing Games")
    except Exception as e:
        print("Exception: " + str(e))
        print(e.args)
        time.sleep(1)
        pass
