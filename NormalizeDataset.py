from math import ceil, log1p

#open files to read from and write to
readfile = open("rosterFIXED.csv", "r")
file = open("rosterLnNORMALIZED.csv", "w", 1)
file.write(
    "Summoner Name,Summoner Id,Summoner Level,Champion Name,Champion Id,Mastery Points,Normalized Mastery Points,Mastery Level,Last Played Acc Date,Last Played Champ Date\n")

summoners = {}
header = True
for line in readfile:
    #skip header
    if header:
        header = False
        continue

    data = line.split(',')

    #Normalization method here
    if data[1] in summoners.keys():
        #Natural Log Version
        normalizedpoints = ceil(log1p(int(data[5])) / summoners[data[1]] * 100)

        #Straight Normalized
        #normalizedpoints = ceil(log1p(int(data[5])) / summoners[data[1]] * 100)

    else:
        normalizedpoints = 100
        #Natural Log Version
        summoners[data[1]] = log1p(int(data[5]))

        #Straight Normalized
        #summoners[data[1]] = log1p(int(data[5]))

    #write text to file
    text = "{SummonerName},{SummonerId},{SummonerLevel},{ChampionName},{ChampionId},{MasteryPoints},{MasteryPointsNormalized},{MasteryLevel},{LastPlayedAcc},{LastPlayedChamp}".format(
        SummonerName=data[0],
        SummonerId=data[1],
        SummonerLevel=data[2],
        ChampionName=data[3],
        ChampionId=data[4],
        MasteryPoints=data[5],
        MasteryPointsNormalized=normalizedpoints,
        MasteryLevel=data[6],
        LastPlayedAcc=data[7],
        LastPlayedChamp=data[8])
    print(text)
    file.write(text)
