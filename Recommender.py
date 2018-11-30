import math
from surprise import Reader, Dataset
from surprise import SVD
from collections import defaultdict

def read_ratings_from_file(file):
    rating_array = []
    file_reader = open(file, "r")
    header = True
    for line in file_reader:
        if header:
            header = False
            continue
        line_array = line.split(',')
        user = line_array[1]
        user_name = line_array[0]
        champion = line_array[4]
        champion_name = line_array[3]
        cmp = int(line_array[6])
        rating_array.append({"User": user_name, "Champion": champion_name, "CMP": cmp})
    return rating_array


def pull_champ_ratings(champion, rating_array):
    champ_ratings = []
    for rating in rating_array:
        if rating['Champion'] == champion:
            champ_ratings.append(rating)
    return champ_ratings


def pull_user_ratings(user, rating_array):
    user_ratings = []
    for rating in rating_array:
        if rating['User'] == user:
            user_ratings.append(rating)
    return user_ratings


def rating_difference(rating, rating2):
    diff = rating['CMP'] - rating2['CMP']
    return diff if diff >= 0 else diff * -1


def user_rating_difference(champ, user1_ratings, user2_ratings):
    if len(pull_champ_ratings(champ, user1_ratings)) == 0:
        return math.inf
    if len(pull_champ_ratings(champ, user2_ratings)) == 0:
        return math.inf
    return rating_difference(pull_champ_ratings(champ, user1_ratings)[0], pull_champ_ratings(champ, user2_ratings)[0])


def champ_rating_difference(champ_ratings, user1, user2):
    if len(pull_user_ratings(user1, champ_ratings)) == 0:
        return math.inf
    if len(pull_user_ratings(user2, champ_ratings)) == 0:
        return math.inf
    return rating_difference(pull_user_ratings(user1, champ_ratings), pull_user_ratings(user2, champ_ratings))


def get_top_n(predictions, n=3):
    '''
    Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    '''

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

ratings = read_ratings_from_file('rosterNORMALIZED.csv')
# Rating table should be {User, Champion, CMP}

#for rating in ratings:
#    print(rating)


#for rating in pull_user_ratings('GankedByNausea', ratings):
#    print(rating)

saladratings = pull_user_ratings('GankedByNausea', ratings)
dylratings = pull_user_ratings('Thenotsocoolkid', ratings)
print(pull_champ_ratings('Amumu', dylratings))
print(pull_champ_ratings('Amumu', saladratings))
print(user_rating_difference('Amumu', dylratings, saladratings))

# Define the format
reader = Reader(line_format='user item rating', sep=',',rating_scale=(1.0,5.0),skip_lines=1)
data = Dataset.load_from_file('final_roster.csv', reader=reader)
print(data)
trainset = data.build_full_trainset()
algo = SVD()
print("algo made")
algo.fit(trainset)
print("algo fitting")
testset = trainset.build_anti_testset()
print(trainset)
predictions = algo.test(testset)
exit(0)
top_n = get_top_n(predictions)

# Print the recommended items for each user
for uid, user_ratings in top_n.items():
    print(uid, [iid for (iid, _) in user_ratings])
#
# userid = str(97999132)
# itemid = str(21)
# actual_rating = 4.89
# print(algo.predict(userid, itemid, actual_rating))
# #for rating in pull_champ_ratings('Xin Zhao', ratings):
#     #print(rating)