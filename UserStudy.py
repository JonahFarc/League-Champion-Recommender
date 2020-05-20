import math
import random
from random import randint
from surprise import Reader, Dataset, SVD
from collections import defaultdict

import pandas as pd
import requests
from surprise.model_selection import train_test_split

from modules.Recommender import recommend

url_base = "https://na1.api.riotgames.com/lol/"
url_mastery = "champion-mastery/v3/champion-masteries/by-summoner/"
url_summ_name = "summoner/v3/summoners/by-name/"
API_KEY = "REMOVED"

roster = 'datasets/user-study-roster.csv'
max_champs = 5
num_predictions = 5  # set to 'max' to return all predictions in descending order

champ_map = {'266': 'Aatrox', '103': 'Ahri', '84': 'Akali', '12': 'Alistar', '32': 'Amumu', '34': 'Anivia',
             '1': 'Annie', '22': 'Ashe', '136': 'Aurelion Sol', '268': 'Azir', '432': 'Bard', '53': 'Blitzcrank',
             '63': 'Brand', '201': 'Braum', '51': 'Caitlyn', '164': 'Camille', '69': 'Cassiopeia', '31': "Cho'Gath",
             '42': 'Corki', '122': 'Darius', '131': 'Diana', '119': 'Draven', '36': 'Dr. Mundo', '245': 'Ekko',
             '60': 'Elise', '28': 'Evelynn', '81': 'Ezreal', '9': 'Fiddlesticks', '114': 'Fiora', '105': 'Fizz',
             '3': 'Galio', '41': 'Gangplank', '86': 'Garen', '150': 'Gnar', '79': 'Gragas', '104': 'Graves',
             '120': 'Hecarim', '74': 'Heimerdinger', '420': 'Illaoi', '39': 'Irelia', '427': 'Ivern', '40': 'Janna',
             '59': 'Jarvan IV', '24': 'Jax', '126': 'Jayce', '202': 'Jhin', '222': 'Jinx', '145': "Kai'Sa",
             '429': 'Kalista', '43': 'Karma', '30': 'Karthus', '38': 'Kassadin', '55': 'Katarina', '10': 'Kayle',
             '141': 'Kayn', '85': 'Kennen', '121': "Kha'Zix", '203': 'Kindred', '240': 'Kled', '96': "Kog'Maw",
             '7': 'LeBlanc', '64': 'Lee Sin', '89': 'Leona', '127': 'Lissandra', '236': 'Lucian', '117': 'Lulu',
             '99': 'Lux', '54': 'Malphite', '90': 'Malzahar', '57': 'Maokai', '11': 'Master Yi', '21': 'Miss Fortune',
             '62': 'Wukong', '82': 'Mordekaiser', '25': 'Morgana', '267': 'Nami', '75': 'Nasus', '111': 'Nautilus',
             '76': 'Nidalee', '56': 'Nocturne', '20': 'Nunu & Willump', '2': 'Olaf', '61': 'Orianna', '516': 'Ornn',
             '80': 'Pantheon', '78': 'Poppy', '555': 'Pyke', '133': 'Quinn', '497': 'Rakan', '33': 'Rammus',
             '421': "Rek'Sai", '58': 'Renekton', '107': 'Rengar', '92': 'Riven', '68': 'Rumble', '13': 'Ryze',
             '113': 'Sejuani', '35': 'Shaco', '98': 'Shen', '102': 'Shyvana', '27': 'Singed', '14': 'Sion',
             '15': 'Sivir', '72': 'Skarner', '37': 'Sona', '16': 'Soraka', '50': 'Swain', '134': 'Syndra',
             '223': 'Tahm Kench', '163': 'Taliyah', '91': 'Talon', '44': 'Taric', '17': 'Teemo', '412': 'Thresh',
             '18': 'Tristana', '48': 'Trundle', '23': 'Tryndamere', '4': 'Twisted Fate', '29': 'Twitch', '77': 'Udyr',
             '6': 'Urgot', '110': 'Varus', '67': 'Vayne', '45': 'Veigar', '161': "Vel'Koz", '254': 'Vi',
             '112': 'Viktor', '8': 'Vladimir', '106': 'Volibear', '19': 'Warwick', '498': 'Xayah', '101': 'Xerath',
             '5': 'Xin Zhao', '157': 'Yasuo', '83': 'Yorick', '154': 'Zac', '238': 'Zed', '115': 'Ziggs',
             '26': 'Zilean', '142': 'Zoe', '143': 'Zyra'}
summoners = {}

while True:
    summ_name = input("What is your summoner name?\n")
    recommendations, mastery = recommend(API_KEY, summ_name, max_champs, num_predictions, roster)
    if recommendations is "ERROR":
        print("Error pulling from Riot API")
        exit(1)

    unavailable_items = []
    output = ""
    for mastery_id in mastery:
        unavailable_items.append(str(mastery_id))

    for uid, user_ratings in recommendations.items():
        rec_champs = []
        mixed_champs = []
        output += "So I recommend: "
        for (iid, _) in user_ratings:
            mixed_champs.append(iid)
            unavailable_items.append(str(iid))
            output += champ_map[str(iid)] + ", "
            rec_champs.append(iid)
        output = output[:-2] + "\n"
        output += "Random champions: "
        count = 0
        while count < num_predictions:
            champid, champname = random.choice(list(champ_map.items()))
            if champid not in unavailable_items and int(champid) not in mixed_champs:
                count += 1
                output += champname + ", "
                mixed_champs.append(int(champid))
        output = output[:-2] + "\n"
        random.shuffle(mixed_champs)
        output += "Mixed list: \n"
        index = 1
        for champ in mixed_champs:
            output += str(index) + ". " + champ_map[str(champ)]
            output += "*\n" if champ not in rec_champs else "\n"
            index += 1
        print(output + "\n")