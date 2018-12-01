from math import log1p

#open files to read from and write to
readfile = open("rosterNORMALIZED.csv", "r")
file = open("final_roster2.csv", "w", 1)
file.write(
    "Summoner Id,Champion Id,Normalized Mastery Points\n")
summoners = {}
header = True
for line in readfile:
    #skip header
    if header:
        header = False
        continue

    data = line.split(',')

    #write text to file
    text = "{SummonerId},{ChampionId},{MasteryPointsNormalized}\n".format(
        #SummonerName=data[0],
        SummonerId=data[1],
        #ChampionName=data[3],
        ChampionId=data[4],
        #MasteryPoints=data[5],
        MasteryPointsNormalized=data[6])
    print(text)
    file.write(text)
