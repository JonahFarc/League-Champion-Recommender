import time
import datetime
import requests

def build_dataset(API_KEY, file_path, iterations):
    # Hardcoded URL variables
    url_base = "https://na1.api.riotgames.com/lol/"
    url_mastery = "champion-mastery/v3/champion-masteries/by-summoner/"
    url_summ_name = "summoner/v3/summoners/by-name/"
    url_feat_games = "spectator/v3/featured-games"
    url_version = "https://ddragon.leagueoflegends.com/realms/na.json"

    # Create a champion map to map the champion's id number to their name
    champ_version = requests.get(url_version).json()["n"]["champion"]
    champ_map = {}
    champ_response = requests.get("http://ddragon.leagueoflegends.com/cdn/" + champ_version + "/data/en_US/champion.json")
    champ_json = champ_response.json()
    for champ in champ_json["data"].keys():
        champ_map[champ_json["data"][champ]["key"]] = champ_json["data"][champ]["name"]

    # open file to write to
    file = open(file_path, "a", 1)
    # file.write(
    #     "Summoner Name,Summoner Id,Summoner Level,Champion Name,Champion Id,Mastery Points,Mastery Level,Last Played Acc Date,Last Played Champ Date\n")
    used_summoners = []

    # Loop until program manually exited
    for _ in range(0, iterations):
        try:
            # Get list of featured games by riot's API
            specurl = url_base + url_feat_games + "?api_key=" + API_KEY
            spec_response = requests.get(specurl)
            spec_json = spec_response.json()

            # Loop through each player in each game
            for game in spec_json["gameList"]:
                for player in game["participants"]:
                    # check to see if player is currently being used or not
                    playerid = player["summonerName"]
                    if playerid in used_summoners:
                        continue
                    used_summoners.append(playerid)

                    # Pull info about the summoner
                    summ_url = url_base + url_summ_name + str(playerid) + "?api_key=" + API_KEY
                    summ_response = requests.get(summ_url)
                    # print("Summoner response code: " + str(summresponse.status_code))
                    summ_json = summ_response.json()
                    print("Summoner Json: " + str(summ_json))
                    maxInactivityTime = 31556952000  # milliseconds in One Year
                    if summ_response.status_code != 200:
                        print("Error: Status Code: " + str(summ_response.status_code))
                        continue
                    if len(summ_json) == 0:
                        print("Error: Empty Summoner JSON response")
                        continue
                    if summ_json["summonerLevel"] < 30:
                        print("Error: Summoner {name} is too low leveled!".format(name=summ_json["name"]))
                        continue
                    if (int(round(time.time() * 1000)) - summ_json["revisionDate"]) < maxInactivityTime:
                        print("Error: Summoner{name} has been inactive for too long!".format(name=summ_json["name"]))
                        continue
                    summonerid = summ_json["id"]

                    # Pull information about champion mastery from riot API
                    mast_url = url_base + url_mastery + str(summonerid) + "?api_key=" + API_KEY
                    mast_response = requests.get(mast_url)
                    # print("Mastery response code: " + str(mastresponse.status_code))
                    mast_json = mast_response.json()
                    print("Mastery Json: " + str(mast_json))
                    # print mastery values to file for each champion
                    for x in range(0, len(mast_json)):
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

API_KEY = "REMOVED"
file_name = 'datasets/roster.csv'
iterations = 3000

if __name__ == "__main__":
    build_dataset(API_KEY,file_name,iterations)