from math import log1p

def format(file1, file2):
    #open files to read from and write to
    readfile = open(file1, "r")
    file = open(file2, "w", 1)
    file.write(
        "Summoner Id,Champion Id,Normalized Mastery Points\n")
    summoners = {}
    header = True
    max = 3
    count = 0
    for line in readfile:
        #skip header
        if header:
            header = False
            continue

        data = line.split(',')
        if data[1] not in summoners:
            count = 1
            summoners[data[1]] = data[0]
        elif count > max:
            continue
        else:
            count += 1
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


format("normalized_roster.csv", "final_roster.csv")