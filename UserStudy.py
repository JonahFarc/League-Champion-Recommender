import math
import random
from random import randint
from surprise import Reader, Dataset, SVD
from collections import defaultdict

import pandas as pd
import requests
from surprise.model_selection import train_test_split

url_base = "https://na1.api.riotgames.com/lol/"
url_mastery = "champion-mastery/v3/champion-masteries/by-summoner/"
url_summ_name = "summoner/v3/summoners/by-name/"
API_KEY = "RGAPI-fe8e85f4-572e-41b0-94bc-7ad2dbb1c847"

roster = 'user-study-roster.csv'
max_champs = 5
num_predictions = 5  # set to 'max' to return all predictions in descending order
num_random_champs = 5

def get_mastery_from_id(summonerid, max_champs):
    """
    Pulls the Mastery information from Riot's API, the top 5 champions of the summoner,
    and their normalized mastery points

    :param summonerid: id of summoner to pull information from
    :param max_champs: maximum number of champs to pull mastery from
    :return: dictionary containing top 5 champions and their normalized mastery points
    """
    # Pull information about champion mastery from riot API
    mast_url = url_base + url_mastery + str(summonerid) + "?api_key=" + API_KEY
    mast_response = requests.get(mast_url)
    mast_json = mast_response.json()

    # Ensure valid response from server
    if mast_response.status_code != 200:
        print("Error pulling player from server!")
        return "ERROR"

    # Ensure player has mastery points
    if len(mast_json) == 0:
        print("Player has no mastery!")
        return "ERROR"

    # File mastery values for top max_champs champions
    max_points = 0
    ratings_dict = {'userID': [], 'itemID': [], 'rating': []}
    for x in range(0, min(len(mast_json), max_champs)):
        if x == 0:
            max_points = mast_json[x]["championPoints"]
        normalized_points = math.ceil(int(mast_json[x]["championPoints"]) / max_points * 100)
        ratings_dict['userID'].append(summonerid)
        ratings_dict['itemID'].append(mast_json[x]["championId"])
        ratings_dict['rating'].append(normalized_points)
    return ratings_dict

def get_mastery(summonername, max_champs):
    """
    Gets the summoner id of the player with the given summoner name and their dictionary
    from get_mastery_from_id

    :param summonername: name of the summoner to pull information of
    :param max_champs: maximum number champions to pull mastery of
    :returns: summonerid, ratings_dict: ID of the summoner, dictionary containing normalized masteries of the summoner's top 5 champions
    """
    # Pull info about the summoner
    summ_url = url_base + url_summ_name + summonername + "?api_key=" + API_KEY
    summ_response = requests.get(summ_url)
    summ_json = summ_response.json()

    # Ensure valid status code
    if summ_response.status_code != 200:
        print("Error pulling player from server!")
        return 1, "ERROR", 1

    # Ensure return isn't empty
    if len(summ_json) == 0:
        print("Error: Empty Summoner JSON response")
        return 1, "ERROR", 1

    summonerid = summ_json["id"]
    return summonerid, get_mastery_from_id(summonerid, max_champs), summ_json["name"]

def get_top_n(predictions, n=5):
    """
    Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 5.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        if n == "max":
            top_n[uid] = user_ratings
        else:
            top_n[uid] = user_ratings[:n]
    return top_n

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

# read info from roster
df = pd.read_csv(roster, header=None, names=['userID', 'itemID', 'rating'])
mean = df['rating'].mean()
dfreader = Reader(rating_scale=(1, 100))
# data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], dfreader)
# trainset, testset = train_test_split(data, shuffle=False, test_size=1)
# trainset = data.build_full_trainset()

algo = SVD()
algo.random_state = 1
# print("Generating algorithm... (This may take a while)")
# algo.fit(trainset)
'''
print("Algorithm Generated!")
# define a cross-validation iterator
print("Cross-Validating... (This may take a while)")
kf = KFold(n_splits=3)
for trainer, tester in kf.split(data):
    # train and test algorithm.
    algo.fit(trainer)
    prediction = algo.test(tester)

    # Compute and print Root Mean Squared Error
    accuracy.rmse(prediction, verbose=False)
'''
# print("All ready!")
while True:
    summ_name = input("What is your summoner name?\n")  # "Naru"
    summ_id, ratings_dict, summ_name = get_mastery(summ_name, max_champs)

    # Problem occurred while trying to pull data from Riot API
    if ratings_dict == "ERROR":
        print()
        continue

    # Add summoner name to list
    if str(summ_id) not in summoners:
        summoners[str(summ_id)] = summ_name

    # Add remainder champs to test on
    length = 0
    for champ in champ_map:
        if int(champ) not in ratings_dict['itemID']:
            length += 1
            ratings_dict['userID'].append(summ_id)
            ratings_dict['itemID'].append(int(champ))
            ratings_dict['rating'].append(0)
    dataframe = df.append(pd.DataFrame(ratings_dict))
    data = Dataset.load_from_df(dataframe[['userID', 'itemID', 'rating']], dfreader)
    trainset, testset = train_test_split(data, shuffle=False, test_size=length)

    print("Calculating Champs... (This may take a while)")
    algo.fit(trainset)
    print("Done calculating.")
    # Rating table should be {User, Champion, CMP}
    # Define the format
    # reader = Reader(line_format='user item rating', sep=',',rating_scale=(1, 100), skip_lines=1)
    # data = Dataset.load_from_file('final_roster2.csv', reader=reader)
    # trainset = data.build_full_trainset()

    # testset = trainset.build_anti_testset()

    # Get the results from applying the algorithm to the summoner
    predictions = algo.test(testset, verbose=False)
    top_n = get_top_n(predictions, num_predictions)

    unavailable_items = []
    output = ""
    for x in range(0, len(champ_map) - length):
        unavailable_items.append(str(ratings_dict['itemID'][-(x + length + 1)]))
        output = champ_map[str(ratings_dict['itemID'][-(x + length + 1)])] + ", " + output
    output = output[:-2] + "\n"
    output = "Your top champions are: " + output
    # Print the recommended items for each user]
    for uid, user_ratings in top_n.items():
        rec_champs = []
        # print(summoners[str(uid)], [(champ_map[str(iid)], riid) for (iid, riid) in user_ratings])
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
        while count < num_random_champs:
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
        #output = output[:-2]
        print(output + "\n")