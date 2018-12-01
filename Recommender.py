import math
from surprise import Reader, Dataset, SVD, accuracy
from collections import defaultdict

import pandas as pd
import requests
from surprise.model_selection import train_test_split, KFold

url_base = "https://na1.api.riotgames.com/lol/"
url_mastery = "champion-mastery/v3/champion-masteries/by-summoner/"
url_summ_name = "summoner/v3/summoners/by-name/"
API_KEY = "RGAPI-fe8e85f4-572e-41b0-94bc-7ad2dbb1c847"


def get_mastery_from_id(summonerid):
    """
    Pulls the Mastery information from Riot's API, the top 5 champions of the summoner,
    and their normalized mastery points

    :param summonerid: id of summoner to pull information from
    :return: dictionary containing top 5 champions and their normalized mastery points
    """
    # Pull information about champion mastery from riot API
    mast_url = url_base + url_mastery + str(summonerid) + "?api_key=" + API_KEY
    mast_response = requests.get(mast_url)
    # Ensure valid response from server
    if mast_response.status_code != 200:
        print("Error pulling player from server!")
        return "ERROR"
    # print("Mastery response code: " + str(mast_response.status_code))
    mast_json = mast_response.json()

    # print("Mastery Json: " + str(mast_json))
    # File mastery values for top max_champs champions
    max_points = 0
    max_champs = 5
    ratings_dict = {'userID': [], 'itemID': [], 'rating': []}
    for x in range(0, min(len(mast_json), max_champs)):
        if x == 0:
            max_points = mast_json[x]["championPoints"]
        normalized_points = math.ceil(int(mast_json[x]["championPoints"]) / max_points * 100)
        ratings_dict['userID'].append(summonerid)
        ratings_dict['itemID'].append(mast_json[x]["championId"])
        ratings_dict['rating'].append(normalized_points)
    return ratings_dict


def get_mastery(summonername):
    """
    Gets the summoner id of the player with the given summoner name and their dictionary
    from get_mastery_from_id

    :param summonername: name of the summoner to pull information of
    :returns: summonerid, ratings_dict: ID of the summoner, dictionary containing normalized masteries of the summoner's top 5 champions
    """
    # Pull info about the summoner
    summ_url = url_base + url_summ_name + summonername + "?api_key=" + API_KEY
    summ_response = requests.get(summ_url)
    summ_json = summ_response.json()
    # print("Summoner Json: " + str(summ_json))

    # Ensure valid status code
    if summ_response.status_code != 200:
        print("Error pulling player from server!")
        # print("Error: Status Code: " + str(summ_response.status_code))
        return 1, "ERROR"
    # Ensure return isn't empty
    if len(summ_json) == 0:
        print("Error: Empty Summoner JSON response")
        return 1, "ERROR"
    summonerid = summ_json["id"]
    return summonerid, get_mastery_from_id(summonerid, ratings_dict)


def get_top_n(predictions, n=3):
    """
    Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

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


'''
#Create a champion map to map the champion's id number to their name
url_version = "https://ddragon.leagueoflegends.com/realms/na.json"
champ_version = requests.get(url_version).json()["n"]["champion"]
champ_map = {}
champ_response = requests.get("http://ddragon.leagueoflegends.com/cdn/" + champ_version + "/data/en_US/champion.json")
champ_json = champ_response.json()
for champ in champ_json["data"].keys():
    champ_map[champ_json["data"][champ]["key"]] = champ_json["data"][champ]["name"]

summoners = {}
file = open('rosterLaanNORMALIZED.csv','r')
header = True
for line in file:
    if header:
        header = False
        continue
    data = line.split(',')
    if data[1] in summoners:
        continue
    summoners[data[1]] = data[0]

print(champ_map)
print(summoners)
exit(0)
'''
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
summoners = {'97999132': 'The Comet', '35650213': 'Fawkes Fireforge', '37826988': 'INTER LAN PLAYER',
             '30297138': 'Twinge', '29194631': 'Alicopter', '27796007': 'GGS bobqin', '21273721': 'Forest',
             '28711689': 'tangledbutthairs', '46221759': 'ThalCuVeeADD', '25906242': 'Dykes On Nikes',
             '92909558': 'Ivern Mane', '19577485': 'Paralaize', '44188343': 'Support Puppy', '30003302': 'Donkey Kongo',
             '30109034': 'NotMike', '19477267': 'Wryda', '22761195': 'Mrand Master', '31337969': 'EskiMoe',
             '28442195': 'NUMBER 1 CPU BOT', '19457385': 'SiG Vynn', '37824000': 'Wanzhen', '49681254': 'Chuggz',
             '56551433': 'Montagues', '21380620': 'Gogadantess', '68270128': 'sonicfox117', '22057898': 'Seacrest11',
             '25121596': 'seek refuge', '21776199': 'Ecci', '24053067': 'XLC', '21805921': 'Blessfullangle',
             '31489936': 'Where are u', '70380483': 'QianKunJieFa', '36391972': 'BabyB0kChoy',
             '34871057': 'Vip Monst3r', '39214431': 'TM20n', '47704330': 'MorningGloryHole', '34892423': 'Jerkyx',
             '29251639': 'Alteisen', '43966181': 'ReddGiraffe', '28990767': 'Yung Flex Ñigga',
             '26379627': 'TheJohnGalt', '37793740': 'Mizgarth', '23244019': 'Uchiha Itachi', '41751413': 'stopcraft',
             '25471200': 'castlës', '45252657': 'Benio Adashino', '40631993': 'CreamyCracker',
             '50031282': 'KoolAidManIsCool', '32722885': 'Muuku', '23785209': 'SekaiNoMajou', '40829115': 'Syñc',
             '66170386': 'NSG BlackHuhU', '19667237': 'Pdv Jarcor', '45911607': 'jist04', '31847802': 'Yeoreumie',
             '30074386': 'Actually Kill Me', '68320041': 'FlyLikeACat', '71150461': 'GhøstBlade', '37426086': 'Devom',
             '70281021': 'Meinv', '38025902': 'DerpTheDark', '82669824': 'Con dau bung', '46690626': 'MTail',
             '37858099': 'VenusBomb', '24263976': 'Farstrider Jain', '20756604': 'Humain', '87069356': 'ALLINTHEGAMEHH',
             '44108265': 'xVirtue', '44677371': 'SoCal Trojan', '59734256': 'Healer Flares', '32556358': 'Gamer Girl',
             '22344906': 'Zing', '24197510': 'Ina', '27519370': 'Vase Admirer', '52110518': 'FourGabriel',
             '30413844': 'M4A12', '32456009': 'Puggo', '21485042': 'Master Zeus', '34071861': 'Årcade Poro',
             '38791452': '4gp', '54321283': 'Milky Way Wishes', '32620692': 'Faded Kai', '97681256': 'Lunachrìs',
             '23308955': 'Cherelle', '45420993': 'PunchinelIo', '24192145': 'Ketsuraku', '32277338': 'MonstrGirlsRaepU',
             '63990303': 'la la boo', '93379302': 'Cu Den69', '38261001': 'Milkitty Doubi', '24532583': 'BuBlewBlue',
             '59697762': 'Keitamo', '97549129': 'D OMEGALUL M', '94060086': 'TwTv LoLHarambe',
             '28879891': 'MeWillCureAging', '96039080': 'summer day', '43188251': 'RockBrain Lover',
             '30072007': 'Stronger Mental', '21800248': 'hello apple', '28746413': 'Spikeman666',
             '20487919': 'LightDatz', '37803941': 'RHP Miro', '81289311': 'Bustin Knuts', '20117634': 'Dethnote',
             '71552075': 'CinnabarA', '21686553': 'Staxl', '90292': 'LoOz', '30703674': 'BryceX',
             '23886464': 'Broseph Stalin', '20514130': 'Hataz gotz Lazaz', '80109115': '53620',
             '70609333': 'SuperCarry 53620', '21700711': 'IUº', '28966581': 'Mayari', '19921145': 'nokillme',
             '46225481': 'SGTStrudel', '39635216': 'Cardinxl', '72925228': 'Calibruhtions', '26165756': 'Clare47',
             '21121636': 'cosmicrayon', '51524724': 'SoulSmithy', '59779963': 'Durex gum', '20708684': 'Xanxusw',
             '39400006': 'drager123', '82962745': 'Wystfúl', '19338860': 'Clobek', '93230422': 'supergamer420',
             '42026966': 'ShOoMhEaD', '47768708': 'Hotsauceeeeeee', '78460455': 'Doctor Feelsack',
             '28954633': 'tamagochi434', '26120167': 'Fates Ascension', '50238750': 'beaufl', '30294525': 'HayDenV5',
             '42778686': 'Duràtus', '21978772': 'ClearDays', '35191667': 'SmexyBaker', '30202362': 'ScrewedForLife',
             '169394': 'Raeon', '58505419': 'Redesignated', '36770493': 'Ipodkill', '24141305': 'fkinghighbro',
             '70359148': 'SDzgFdfgy', '86849731': 'qunimadeforever', '55845898': 'simplemonkey1',
             '58463598': 'Fluffy Shenteemo', '37383191': 'CeIsius', '90401160': '06 12 2004', '97912127': 'I Hate Them',
             '82789451': 'Nemësis', '43529631': 'Kolthro', '27479287': 'Auntie Jin', '22110089': 'Deathsheep',
             '51065382': 'Phallusy', '19776516': 'Omnipherious', '89392940': 'BrianYC', '22390224': 'skinnymexijew',
             '40591569': 'TL Iamtheattack', '47829644': 'surveillance0 0', '48195837': 'lil red rideugud',
             '46415323': 'NEET', '70280081': 'dr1nkwater', '53151246': 'Kingdom1997', '54948621': 'cabbysb',
             '45176933': 'Int if Top', '46552004': 'Díos', '24446436': 'JayJurz', '85430634': 'lets go me',
             '65711322': 'EagleSIBAql', '56821156': 'greatboy900', '60217590': 'DU HAI TAO', '59464399': 'Nadooo',
             '30839645': 'TheRickyB', '21240361': 'NeWardog', '53290831': 'Teil', '60491429': 'Mirrorcoat',
             '53146620': 'Wíley', '83961142': 'FFF HDGQ', '58522663': 'Isolate Me Daddy', '26237301': 'Nocchi',
             '89021724': 'DK Hardest Wine', '73259700': 'FK Wildest Dog', '26240778': 'mvpjohnliu',
             '34312780': 'Mikanyo', '27815012': 'Foxxywaffle', '27270885': 'Kihav', '59851836': 'Syces',
             '81291732': 'Hwangbo Jin', '21786910': 'Typos', '45548654': 'N3UROSIS', '19820487': 'Kinzen',
             '70561433': 'Hyöhyö', '35721171': 'Pang BeiBei', '69299482': 'Kahrul', '40823944': 'Oonyxia',
             '20183944': '123abc345', '22854647': 'Ryim', '21499910': 'TeemboKeem', '35122392': 'tqihtoit',
             '44092756': 'FizzDeChienneD32', '22673760': 'Donyoku D32', '30033519': 'Arc Royal',
             '68141946': 'sorta cute', '19551420': 'Smooshedpoop', '35534169': 'Balenciagay',
             '29771974': 'VulvaBaracuda420', '21209063': 'abneezy', '22596934': 'Bloove', '92590620': 'Yubi0211',
             '98780916': 'Blamed One', '98471071': 'biedongF6', '44966917': 'MarsheeMellow', '49275155': 'A S B',
             '47101639': 'CrimsonRaptorQwQ', '82520554': 'zÓÉpÚssyjÜÍcé L9', '48999412': 'DanBBBB',
             '22300325': 'Knoxav', '21245350': 'PianoConspiracy', '90702036': 'IbraMiharbi', '24904235': 'LFFN',
             '38993996': 'Martell', '25779106': 'Exilex', '31372466': 'xEyeMan', '54870891': 'Åll Mîght',
             '45729007': 'Bashful Iceberg', '21684805': 'FailCow17', '43815972': 'Eternalnoobert',
             '35106231': 'Jeroniwhoa', '34963742': 'Gapezilla', '47170002': 'KAI desu', '31301860': 'DoolVl',
             '27723449': 'oOrange', '32154744': 'Kyuki', '32626757': 'TwitchTv Dejann', '34563833': 'Mural',
             '20886395': 'BeNice2EachOther', '86890788': 'l am Izaac', '91151712': 'Kappa Face', '98299264': '1 sun',
             '98903237': 'SWOLEBROS', '35634709': 'God Apple Juice', '51125469': 'Mintie Very Lao',
             '24516433': 'Soggon', '53619632': 'Fred LaTruelle', '83832611': 'Élysian', '95810304': 'Just a ØneTrick',
             '20778097': 'Danijrm', '45117226': 'Greatmimic', '79080215': 'UnitedKoreans', '40027808': 'Rory Mcilroy',
             '28939870': 'danman97', '45261832': 'magicfoodboy', '29593986': 'Èssence', '52424': 'ShorterACE',
             '20153677': 'ah im so hungry', '51752358': 'Quantah', '42251195': 'Sidewinder Six',
             '65194167': 'Tenderness111', '88110372': 'Saint Creazil', '39576049': 'Congelata Unum',
             '91283552': 'DropsFromHeaven', '22299006': 'Ban My Potato', '68520105': 'LetGoMyLegHo',
             '19867972': 'Seasonchamp', '32537845': 'Akios02', '21731999': 'TOnioNY', '29277152': 'jkLOLS',
             '20011678': 'Werelance', '50700022': 'I Lick Markers', '41307359': 'tiin', '24328867': 'IamTheShiet',
             '98259905': 'houe1', '65889974': 'NorthAmericaWolf', '26355148': 'Lu1uu', '81589658': '0iid',
             '43861216': 'the real dodan', '37238124': 'Tixie', '48243217': 'Orsulamon', '38783446': 'AYCE KBBQ',
             '35425702': 'Sikkibahm', '34814408': 'NeonDeFranco', '100099842': 'Asteroidust', '59459500': 'Paper Tlger',
             '40264795': 'er schlaft', '31689053': 'cosekirbii', '87651028': 'Bronze5Bramse', '37440004': 'gamewiz2x3',
             '35190953': 'EnSpire', '81041282': 'Orangebbb', '95092005': 'VetranGhost', '39126965': 'AntoniousMaximus',
             '89281320': 'shellzhou', '33050635': 'Helican', '25262911': 'Yuno Gasai', '72986833': 'P U 5 S',
             '38881364': 'Bong Sensei', '36259712': 'Kamcho', '34380201': 'COME AT ME DUDE',
             '19674554': 'changed my name', '72271982': 'TheGilgamesh', '27169470': 'LotusDrameli',
             '39640478': 'Sarchera', '75820106': 'Twooeggs', '57009992': 'pleeease', '35691763': 'BD CuoZao',
             '89432378': 'BD LuoBen', '82430987': 'CraftyCat3', '61278775': 'Samayo Sora', '47104316': 'Gróot',
             '53752018': 'PLANT BAE', '51483539': 'EuphoricToaster', '470301': 'OMNOMYOURMOM', '21297318': 'JetxSet',
             '73249964': 'IIIIII', '23304763': 'Teemoisthebest', '43374208': 'enlargingcloud',
             '73529966': 'BunnyBuns311', '84300835': 'Eggsache', '37343775': 'luisfepolo',
             '35311215': 'Necromancer Rita', '26157146': 'Willexan', '31983867': 'Kuro no Kenshi', '19958653': 'guntrX',
             '21992879': 'ikHAOTIX', '33060813': 'Ambrose K', '19599092': 'Captain Crabs', '19291712': 'Riyos',
             '82079759': 'ELD Tiny Balls', '81409589': 'Vîktoriâ', '21180554': 'Cruiser', '19397538': 'HisPrincess27',
             '49133212': 'The Suicide', '55865101': 'DownLikeSyndrome', '47524304': '28th February', '21483550': 'pp7',
             '35720571': 'EwinTheBear', '31531690': 'JimmyRustlers', '51110141': 'LoganRT',
             '69823750': 'Full Bokki Desu', '48388315': 'Georgè Pig', '73529695': 'refining', '422502': 'GamersLegends',
             '32627298': 'Pokinee', '97879665': 'SaveHerWolf', '44007196': 'BanBazi', '35911398': 'Deerr',
             '30263247': 'Clarizio', '43592551': '1ucid', '39522497': 'CP Paradox', '47188078': 'Helios6',
             '65602649': 'SparkMyFlames', '42788890': 'xWeepingAngelsx', '34565429': 'Valamarl',
             '84740345': 'ChineseSnakeGuai', '47050590': 'ShOoOm', '57434733': 'The Nebu', '49273037': 'EvntHorizon',
             '54814964': 'Dysipius', '83640378': 'Villliam', '56989203': 'Z3SS', '92979088': 'Best',
             '34037866': 'A New Chapter', '30387623': 'ßardßQ', '52458212': 'Koggle', '48943307': 'Choxobear',
             '25946478': 'TheAntiqueTable', '37844429': 'Sean1352', '24875987': 'AlphaLeo', '24753015': 'Wings Of Fury',
             '23891520': 'SickTality', '43080560': '1nce Again', '34231010': 'I play bad', '34067833': 'PikaFrenzie',
             '52765996': 'Deadruler', '63549666': 'azhongor', '56510517': 'Pizzle 7', '78529486': 'DragoKnight',
             '24598266': 'Gryffin', '51409048': 'lntensity', '70252748': 'sdjs', '41812512': 'DSDW',
             '44199167': 'Ranksta', '21234226': 'ºÛº', '69651713': 'Defenus', '23194590': 'song tou kuangmo',
             '75732917': 'I saw u', '51771130': 'Baky', '20830793': 'TsatsuIow', '13523': 'Flynt Flossy',
             '24948886': 'SquashTurkey', '49010250': 'Im A Dentist', '60255037': 'nagdaddy', '20560782': 'Kaizo Trap',
             '46346299': 'TAGUP Haley', '22689503': 'technovampyre', '44589752': 'Akumapon', '23851799': 'irisia',
             '22500180': 'GGanksBonaqua', '47188483': 'Ishtar Rin', '18985506': 'Beartato', '39513329': 'Charméd',
             '23611387': 'Wuggie', '24800532': 'Mekboss', '26380125': 'Lochinvire', '81803882': 'Wade HenTai',
             '21166546': 'WWWWWWWWWWNWWWWW', '23903300': 'Vivacacious', '32277666': 'AzulCorazon',
             '36651924': 'Sin Acedia', '32694635': 'szx', '62370544': 'Father9', '68609171': 'Pinin Blanc',
             '37411904': 'Mathar', '66864902': '9Mung', '100340479': 'IWD', '296064': '5995',
             '38099532': 'PoppedAndDropped', '25451198': 'Neals', '61918761': 'urfa kebab', '72351437': 'manisa kebab',
             '28761202': 'Angels Demon', '25043832': 'Alnomo', '25549221': 'SphinxterCowboy',
             '89472321': 'A Chinese Jhin', '89244292': 'A chinese Twitch', '21002477': 'Mr Fkin Zee',
             '48355918': '18 Year Old AD', '41719358': '17 Year Old Sup', '71941260': 'De1evan',
             '21834479': 'Is Tenderness', '59993724': 'DESPICABLE KEN', '23643809': 'TEHNAMEOFANOOB',
             '64229279': 'Discount fekar', '75019936': 'Alimuradov', '49919739': 'LeaguerLegend', '56609174': 'Lobu',
             '20682436': 'The Brightt', '92649546': 'icegirl', '30354638': 'cradelzz', '40734513': 'owo kms dab no u',
             '21526490': 'Kermit Sewercide', '23185522': 'Happiness Hotel', '73631776': 'Seczie',
             '80711529': 'OGuiMeat', '25081461': 'diamondbarbie', '20510650': 'oO Scorpz Oo', '23820726': 'Bason',
             '34340312': 'Mamison', '21676368': '0verdrive', '27404643': 'YDHS', '47044255': 'Vinnyg26',
             '55405827': 'No Snowball Plz', '29364614': 'HD PISSJUGS', '71261706': 'Houkii', '20945830': 'Ktotz',
             '38199334': 'StankasaurusDank', '19615750': 'OH SO ARROGANT', '35163629': 'Snípez',
             '42909110': 'Sinbo Hsia', '35440335': 'Mighty Angus', '35312142': 'Jozyy', '41253414': 'loner idiot',
             '38378766': 'WhoknewZeus', '64854698': 'llBeemoll', '61061808': 'Amori', '57009304': 'Dubu Dubu Dubuu',
             '73167604': 'Let Him go', '24383292': 'Vickixiaobaobei', '24502253': 'Rositajonez', '34743513': 'Eyen',
             '35404268': 'Jayshook', '84790791': 'Genis Penius 69', '30124318': 'Xavier99163', '50894275': 'SSMagic',
             '98981513': 'DQZdedie', '42132860': 'C418', '21814435': 'sarumusha', '51702822': 'Dr V0idberg',
             '98519987': 'Toxic Tentacles', '71009452': 'Black puppet', '46125044': 'Tofu Drifter',
             '51026075': 'country329', '37459698': 'Bladeshard', '23680941': 'KKSxOSK', '41913666': 'Rakonus',
             '36696625': 'oizzie', '32854673': 'Casren', '20150201': 'Illyrion', '28776378': 'GenrouTheGhost',
             '20029119': 'Biggybombbay', '19520132': 'BLAMO', '31937770': 'Efflictim', '19169084': 'FremenKnight',
             '93459547': 'A Good Death', '22562227': 'pope of dope', '31242223': 'peacedrop',
             '73970143': 'BleedingDurex', '47291517': 'Meiii', '66149920': 'Kaceeee', '47691717': 'k1ll',
             '79949215': 'Baconpapa', '77630724': 'BaDShyGUy', '69421743': 'CannibalTomato',
             '56399113': 'I AM Qin Shou', '39755772': 'KING OF HAM FTW', '29423936': 'Nightmight', '53016141': '0Iivia',
             '19088377': 'NA Tyrant', '42066560': '92519', '26727450': 'Sebi', '21497252': 'Farefars World',
             '68352055': 'JSiekwia', '19076631': 'Bolduc', '60909401': 'SwagMastaFlex', '26438482': 'Laner',
             '23089539': 'DonDiablitO', '29740260': '30k for Double Q', '22525216': 'Valinor',
             '75103807': 'elmexicanhoe', '48240038': 'YoRS', '35721639': 'Axex', '77033536': 'Cbo',
             '20107587': 'FA Wraith', '25510101': 'SNSD Sunny', '93410808': 'Zolan5', '21328486': 'Vypra',
             '23214393': 'Squid Cub', '34285942': 'W0NKA', '27700563': 'Soohun', '31230470': 'Daker',
             '97821406': 'ajansen', '41338668': 'HexaCat', '21892094': 'Zirful', '37484586': 'iBagtea',
             '76030490': 'HelenaTheBanana', '88912285': 'Arceusrr', '83802588': 'had to do it',
             '67920944': 'big dicc energy', '97560221': 'Don Vito x', '582309': 'smallthin', '22549432': 'shy egirl',
             '41639309': 'Regedice', '53262982': 'I Wont Surrender', '36219700': 'Naruto IRL', '60969084': 'Baegopang',
             '70151537': 'LoveSicknessLxy', '50255736': 'Yonotang', '26873251': 'Philomerces',
             '60744099': 'TheFr3nchMan', '59469688': 'Code Zero Ichigo', '29472109': 'Bbak', '44615585': 'Adrian CF',
             '59910336': 'Ðers', '31775933': 'Lamira', '35332980': 'Lycefur', '42754719': 'Rightful Throne',
             '30066375': 'Lit', '53005454': 'The Play', '53823596': 'Jynxi', '45989930': 'Eàrendil',
             '56890074': 'YoungxDaggerxDik', '70250813': 'CrosisThePurger', '69523573': 'WCH is A SLIIY B',
             '26145040': 'Sunday Silence', '92649512': 'BDD Dog', '22472825': 'Doskoi', '32760165': 'Merra',
             '20128987': 'Manspear', '47754651': 'Amazing Engrave', '60825678': 'I am not a fish',
             '38235696': 'hellohibonjour', '75167': 'z0rz', '22336838': 'MlKEY', '30057018': 'Joanna',
             '67062601': 'TwentyThreeX', '45008310': 'Inebriate', '79872532': 'Larkyy', '32036607': 'Churchyy',
             '70491124': 'NONAMETT', '32203374': 'Øliver Queen', '33330585': 'TheRandomShot',
             '19795978': 'Thick Banana', '25278551': 'MarkCrorigan', '71860178': 'Efz', '89050286': 'Arcade Nami',
             '34941293': 'Take your pills', '92552281': 'riddXX', '26274784': 'linfuguo', '20548431': 'Best Sup Narnia',
             '153261': 'Robocurious', '23208783': 'carotteMAN', '47734234': 'YYyoyodumpling', '21236340': 'l 0pen l',
             '38787805': 'hahafunnyLOL', '44681786': 'IceOnFires', '29558249': 'Nafi', '54569357': 'KaltV',
             '35575174': 'Neros Dragoth', '31976823': 'Headless Kier', '71189107': 'Nadezz',
             '39599769': 'Mars Will DDDD', '41996973': '1232', '91672269': 'foggedftw4', '24851766': 'BrookLon',
             '30345093': 'Enterpool', '47520247': 'CroZZed', '97832334': '9410111231', '38241667': 'WarlockLaw',
             '29266490': 'Skylar135', '50495228': 'HeWhoLiftsTwice', '51409235': 'Gorkyg',
             '35438302': 'SoundwaveCanada', '47789780': 'J J P', '22688425': 'SunnyT', '20962323': 'UncleJeffrey',
             '20712569': 'IamBoshy', '22384903': 'Jestorz', '20270876': 'TwTvlolparnellyx', '27121088': 'KangarooPouch',
             '48211884': 'Sponce', '41069972': 'Reddemon', '54787183': 'Teammate Damage', '49094444': 'Em0Teem0',
             '40031102': 'sex prince', '92779520': 'StarBlitzPlayer', '60821890': 'M only Real C',
             '80830765': 'York moodle', '28888461': 'Chesberry', '73690552': 'MaekawaNya',
             '44432668': 'Gangplanks Waifu', '46075806': 'Hibiki ypaaa', '70230960': 'Hignited1',
             '35112395': 'Ardrayshock', '23696494': 'Valeth', '25589654': 'SmoothBeast', '27861920': 'Classiq',
             '39581389': 'B812', '87309322': 'CornCobNURFace', '56916168': 'Chubster777', '59494175': 'Jonachen',
             '46041891': 'Pûssy', '80029692': 'Bompa', '64774503': 'NEGREDESPRAIRIES', '63688959': '404HookDidntLãnd',
             '35788975': 'Mercury80', '32385899': 'Vikash', '24410120': 'Serc', '19869152': 'Svdx',
             '31412153': '6 ft 3', '35054367': 'KodaChrome', '89551697': 'Nadeko Fan', '26660154': 'Roll it Up',
             '45235434': 'Lv 100 Cubone', '68739117': 'TheGreenApostle', '31721106': 'Demux',
             '55453909': 'Ashadyshadow', '75203830': 'scv131', '19841398': 'Choppes the brv', '47749731': 'LinRin',
             '48704323': 'KelseyMyBaby', '19261767': 'Cedrics', '19825770': 'Sven Von Liftsht', '50642961': 'yangvayne',
             '50638819': 'Rhiming Mariner', '34930058': 'Governor Jones', '39889556': 'Ghaith',
             '70061893': 'Shaun Akuma', '22626716': 'Tinashe', '41020809': 'Cutie Shy Guy', '64231060': 'Sharie',
             '80540309': 'Unreal Goldfish', '20423735': 'Shadrowne', '51329303': 'Stãrdust',
             '48578943': 'C9 BunnyPuPuu', '51913200': 'Commander Ekul', '31313946': 'Shafin', '24985150': 'Nvrirl',
             '38038534': 'KARMA IIMMX', '34769385': 'Huck Fochman', '59658387': 'Varus is Yaoi',
             '72631356': 'Soul For 5', '32443991': 'lJordan', '48531603': 'JpcThundersword',
             '39774920': 'Seamen on Ice', '58132597': 'Choirboysquirrel', '55505292': 'Monsieur Keso',
             '76039147': 'Just a Thought', '34679876': 'MlgMyth', '31489309': 'QR Montreal', '43375124': 'misterdaoust',
             '47719226': 'PiratesZ', '99141409': 'EIGHT NINE THREE', '32198225': 'Ixl Pain lxl',
             '24151270': 'Fattymojo', '29249541': 'CrypticKillertg', '77003305': 'BaboØ71', '66782649': 'dwater',
             '35670422': 'lnfideI', '28099584': 'Skeith The Third', '50645400': 'Cookie Pizza',
             '46851401': 'No RuPaulogies', '40986735': 'ThisSexyBeast', '40257271': 'Helodsaibd',
             '21069746': 'Hidden Nation', '124174': 'Yota', '80821558': 'Hide From MyTeam', '22687934': 'Mr Bond',
             '41195525': 'alphabluesquad', '22551644': 'Elysia Evaine', '30541584': 'crusher2009',
             '80782478': 'DearRoeDeer', '35852780': 'go4ino', '64795591': 'CreationTNT', '40723223': 'Cuddling Tzuyu',
             '39049918': 'radXmobile', '90803162': 'stillah', '29210581': 'Jolty', '26282219': 'ffsDilbert',
             '21134311': 'Skid', '58352096': 'Deathnate129', '30958048': 'ImProudOfYou', '41353792': 'Lycan Leo',
             '39850203': 'Kiritani Hana', '48345505': 'ur face is dum', '29813585': 'Jm9 LoneYeeChan',
             '42737059': 'Jm9 CaiJianPei', '61557725': 'derStoveR', '42099085': 'Jesophat',
             '72952130': 'nEeKo NeEk0 nli', '68659872': 'double0lemon', '25183570': 'Tempestarii',
             '22001141': 'King of 1v1', '37142357': 'Cugi', '72572911': 'SirFireCrotch', '45252638': 'NearRed5',
             '24302648': 'Maro8rice', '20939251': 'Zonrah', '48635519': 'Zeoo Po', '69632452': '17Rogue17',
             '34176902': 'DarakVader', '56351231': 'ecp12', '35744381': 'Renae', '35980406': 'Manwolf',
             '33321689': 'Meowrá', '52680248': 'C9 Senor', '77019170': 'FaIco Master 3K', '278200': 'Smash with Vidan',
             '37234943': 'River King', '55950833': 'Le Sein Bae', '26858025': 'EVilDamn', '593917': 'Zemial',
             '34851252': 'nebs', '56437912': 'doofee3', '67063830': 'Holychild', '30976472': 'Kr1sys',
             '46340248': 'VarienX', '30219453': 'Gundam Flauros', '21896853': 'thndrchunky', '26634640': 'beefstew00',
             '22435969': 'SinsWraths', '29433816': 'Pòkey', '44290326': 'Wolf Marquis', '55922006': 'Boneless Gragas',
             '32519934': 'Viraldi', '36659461': 'DoubleE17', '82681464': 'Zxzi', '23434891': 'Volsing',
             '25130531': 'Ultron 616', '20854259': 'Peeekachuu', '20415879': 'Tree', '40867748': 'K42FTW',
             '99189485': 'AIInamesRtaken', '23886067': 'Kimence', '80079315': 'sha zi', '23412412': 'Hey I am God',
             '59473381': 'CryingShrimp', '335298': 'Teerev', '24772951': 'Rice Supply', '61928968': 'Virimanthas',
             '44857385': 'Ultéar', '26254607': 'Zenedin', '37081469': 'Óbi', '72140609': 'KingWavy1',
             '19247037': 'ASMT', '57589532': 'imsmelly2010', '59389288': 'simbahart11', '28475785': 'Praxis',
             '22866425': 'FYC Prism', '46435675': 'Jotna Sibal', '53343126': 'Duélist', '31919685': 'sleds',
             '44055045': 'Dà Rou Bao', '30454711': 'tomadoe', '50142597': 'Legionigma', '45632776': 'ThatSoTroll',
             '89272999': 'BIackoracle', '58072327': 'Honey HowI', '68662180': 'A Super Teemo', '79859988': 'Mrs Sylvie',
             '24900556': 'Canien', '24860262': 'AlphaQRough', '36395064': 'Prexzer', '51919764': 'And So It Goes',
             '66580155': 'TheLostSoul101', '76139323': 'theoneandonlyr', '21887515': 'Archelord',
             '26353153': 'Meocon35', '25806088': 'AutumnLeafJoshua', '333917': 'ZixacunX', '31019107': 'Ghooni',
             '46057756': 'ssquire14', '29272370': 'Ørnstein', '22007770': 'TheTurdBurgIar',
             '22864374': 'Lord Chihuahua', '51803431': 'Hi im Mas', '28378203': 'Drium', '39680403': 'DamnHomie',
             '27393106': '12A1313IT', '39026936': 'The Final Shunpo', '72632029': 'weegg', '19075761': 'The Distillers',
             '30098089': 'BaoBao Won', '19170050': 'ARAMKUSHLORD', '19952146': 'Thâne', '19559075': 'Slzzler',
             '22353061': 'Pestilus', '27840249': 'Deja Mooo', '44283111': 'Pro x 2Good', '34904978': 'haneure',
             '25073939': 'AlphaCake', '30315863': '100000000000', '39681596': 'Polarîs', '40101989': 'Jblz',
             '21258743': 'ThisGameisAwful', '93670352': 'Kammil', '67165805': 'Dez Deku Nuts',
             '70002697': 'FromLinesOfRed', '22504930': 'JackerNaught', '45176609': 'Amphy', '91151675': 'Miss You All',
             '26295769': 'kyoshio', '35400880': 'AxelsFinalFlame', '25758895': 'Z4DDY', '21585048': 'Rifts Wrath',
             '22373049': 'Chunimasu', '33439727': 'Aeriya', '23742386': 'Soi Con Lupo', '28781420': 'iCommander',
             '46683213': 'Scuttle', '40036366': 'ShadowoftheRosé', '61965598': 'ATARI 2600 E T', '48137021': 'Nechozki',
             '43423748': 'ErosProxy', '39024451': 'fdagkjnhdfkjgskl', '24518752': 'dglins93',
             '49630778': 'BananaSplits', '68023242': 'RektItRalf', '38915591': 'BBmartinez', '40170916': 'Hollows',
             '86850331': 'Playman Cartier', '44872171': 'FlyingPanda', '30611075': 'raodawgzz',
             '71710138': 'Yoruichi82', '21086104': 'plzforgiv3', '76349682': 'zerval', '36551708': 'I AM WORLD ENDER',
             '19656423': 'Dafreakz', '93671195': 'CloudRemake', '95920684': 'Wowzerow', '51889560': 'bashamo',
             '42831230': 'Twtv Blanksterz', '26860210': 'Vaenicus', '32041531': 'AIive', '23604153': 'cizaf',
             '72941790': 'Stupid Won', '44214725': 'Mizore', '37123134': 'M2K', '30460486': 'LilMissRed',
             '18978420': 'Lord Poo Ping', '31520284': 'IsThisL0ss', '47350865': 'terryliao', '57601119': 'Leon Etoile',
             '68229588': 'JewManSavage', '60303452': 'xTruffleShuffle', '54271076': 'SPACETREX', '37482317': 'snowdewd',
             '36352179': 'ThisWasSpace', '38583955': 'Stokers Chew', '43733099': 'Dirty ThreshLite',
             '84699837': 'TripleManny', '32271838': 'NOISIA777', '19510067': 'trickyjello', '22145225': 'Sakkey',
             '66032328': 'wakamax', '81754823': 'Deadpool206303', '81803622': 'Mustard Bread', '30279175': 'nmnlol',
             '34019240': 'Charon Hyades', '92600610': 'mattathiah', '25240956': 'GodDamnedBatman',
             '90763654': 'ShinodaChan', '28844834': 'BD ChouYan', '34582626': 'An Urban Legend',
             '25071620': 'FluffyTheUnicorn', '33790208': 'Cylince', '87219669': 'pNOwOBn', '72450233': 'M4AI',
             '67026126': 'user25790', '41795927': 'BIZAAR NINJA', '51438931': 'FindingLost',
             '41793949': 'girl i hear sumn', '49962216': 'Rommelgnr', '20650896': 'jewbs', '43588557': '88kebyte',
             '35650126': 'naixiaobumo', '69093060': 'NeëkoLove', '22543526': 'Ketsunoana', '25427710': 'Baedrian',
             '37826453': 'PrayingMantitss', '31671261': 'Doomedaim', '49125450': 'hakeKfOTQ2', '39185609': 'Merodiya',
             '91488297': 'lasquez', '100571288': 'Honor TBudd', '74559553': 'Big jellyfish', '55821960': 'FSP P1 Fries',
             '53850522': 'zay123456', '28932905': 'SlowIy', '30449392': 'Greengummy', '35330196': 'nagorb24',
             '42850124': 'NAsFinest', '20502831': 'Dominikachu', '72181635': 'SHE LI MIAN BA', '57409574': 'ßreakfast',
             '35425715': 'Modrick', '73939953': 'Khaleesi Luna', '19638681': 'Tankbeast', '59440345': 'GalvatinoDa2nd',
             '55402749': 'TheMambaMachine', '57429709': 'JuIIian', '54849332': 'IG ccindyindy',
             '36365325': 'AirBudGoldenRec', '36101795': 'FX Hon', '36771787': 'JMeister790', '30241814': 'Acloudis',
             '30680313': 'IIZANDERII', '38877775': 'Young Adrian', '20433369': 'Sitting at Desk',
             '40919682': 'darkfangnight', '40873141': 'Ahlkos24', '22018099': 'M4ST3RD0K4R', '70641846': 'JYSJYS',
             '41776742': 'maxguner', '40112602': 'YouMadCuz2Dads', '91332269': 'NCHammerXD',
             '41316629': 'Shadowbeatsinc', '25017458': 'Lsei', '36633356': 'RainBow3', '34997590': 'Trollobuscus',
             '41892032': 'Wæk', '39292115': 'Alphastar', '45729548': 'DecimateFF', '32151606': 'DCC Salty',
             '23071078': 'Memzonn', '22627890': 'Ivypanda', '20584967': 'Number21And24', '55882938': 'Zerzexx',
             '40181723': 'Dánkplañk', '51480244': 'Immolation', '59733737': 'Jack Vessaluse', '50051050': 'ReusBVB',
             '59143584': 'Oeluz', '343201': 'Mijomon', '29288320': 'DrRubik', '39874233': 'Väyñê',
             '40756021': 'Cthuturu', '76381913': 'TasteMyPlug', '21072211': 'Bao Bao Bandit', '22976890': 'Capndodo',
             '44783215': 'Kirsten', '34289279': 'DBchamberSH', '32854812': 'Dogma of Hell', '21324275': 'dryspark',
             '59296186': 'TheSoapstah', '64181258': 'lephisolophe', '24738418': 'THCZeek',
             '59400536': 'vayne to masters', '86009163': 'Dyna2ty', '61549140': 'pham0us217',
             '49973384': 'I Keep It PG13', '98939157': 'Nyxnemesis', '24003724': 'Galxc', '25240205': 'Langoo',
             '82904621': 'able16', '36341044': 'ThaineBednar', '29587502': 'LordNokren', '83121649': 'PlankedInTheGang',
             '39867028': 'SuperThig', '47107137': 'lll TLT lll', '32401620': 'Hl im Groot', '65312945': 'Nerfed Vayne',
             '35081464': 'Rikka', '86519167': 'Darkkarma4268', '58624950': 'NiuLuKu', '46641587': 'JuanWin',
             '44155592': 'Century', '19189843': 'Jagras', '50649709': 'Kennny', '80952663': 'SALESMANOTHEYEAR',
             '26215088': 'PilltoverJB', '20039686': 'PAPA GIRTH', '21162691': 'Turkeyboy', '19953182': 'Dsler',
             '27436593': 'Lynnie Patootie', '30159029': 'Merlin7795', '32424368': 'XiaoYunTun96',
             '30603155': 'Morshoes', '48243479': 'Zoneray', '71581513': 'Light Chasers 1', '82966929': 'ZuriKat',
             '40590863': 'Sterner Stuff', '60559712': 'David Zhang01', '34969649': 'Fake Vault 13',
             '23096262': 'Bigheartman', '48659178': 'GOD SEND HELP', '47843504': 'Met', '42750485': 'FOUR LOKO FRIDAY',
             '61845157': 'SheLeft 11 14 17', '44805658': 'Meslo', '24621988': 'Xilyana', '21991566': 'FiD Apocalypse',
             '59678716': 'coolguy4000', '24546183': 'MicMac', '24324252': 'GodSpeedY', '539761': 'KelpCho',
             '22178231': 'Bocahz', '24467579': 'Rolf', '23133495': 'AGGYCHEN', '66994293': 'Attinat',
             '34502535': 'Hella Aesthetic', '19761072': 'Xmithie', '36430632': 'Mahir', '43232699': 'Pansie',
             '21446650': 'Varsix', '80732343': 'sry mymistakeTnT', '87599515': 'TwtchTvKarasmai',
             '75649106': 'whitelotuSx1', '64790060': 'PSU KIS0', '45583316': 'Buttersock', '34301929': 'Furry Peaches',
             '42034762': 'Zorenith', '49074241': 'iTubZooNraug', '34441188': 'Corpus', '91251074': '0yiliduo0',
             '23430803': 'The EZ Genius', '19188966': 'Aiona', '20240298': 'a cute idiot', '23826080': 'SpooderMen',
             '40828505': 'Ledatic', '34057632': 'Summ Tingg Wong', '23521666': 'LIFES A TRIP', '24991801': 'Wolfsquad',
             '23727607': 'Ghost of Razgriz', '99253294': 'ProwI', '43589790': 'OrbtlFrme Anubis',
             '68553334': '2Sdragon', '31660209': 'RuPaulogize', '20298222': 'Aneur', '25984666': 'SeaWhores',
             '55549505': 'Cheritiy', '47504850': 'WLotus', '23140073': 'Bregothor', '79320961': 'potato name',
             '29513156': 'xElementalist', '72946397': 'Slefish Xu', '37127929': '1nept', '19908928': 'Safear',
             '91543724': 'Hi Rez Androxus', '19131193': 'zentelia', '35502431': 'iCeMoONk', '19587720': 'Zenic',
             '45006074': 'jarze', '52276221': 'bzz', '39512997': 'Our Team', '26452598': 'Jiorijo',
             '83039168': 'nut lover', '51923303': 'iSmokeMore', '32508736': 'Demeulemeester', '66902127': 'sirBullet13',
             '62139922': 'NYPD warning', '48479300': 'FELLAR', '40665956': 'HennesseyVenomGT', '23977122': 'vennux',
             '58810437': 'ducidni1', '47536855': 'SIFV Pirate', '20604098': 'SinStriker', '23299269': 'GoldBranner',
             '23365512': 'TheLastMan', '65219641': 'LunaLoveWX', '41274882': 'imaQTeapie', '49339976': 'i is Godlike',
             '26241972': 'UTouchMeLolol', '71111297': 'NUTPUNCHER32', '30750186': 'Moenic',
             '82848738': 'ThatVendettaGuy', '34129359': 'SaItbender', '62674082': 'Oblivion Sender',
             '71760383': 'Zells1994', '67096373': 'caoliang', '20531652': 'QuicknToast', '36439650': '401EastToToronto',
             '24511544': 'Warfish', '91411554': 'KoriIakkuma', '40293923': 'Royanik', '47067140': 'Suiri',
             '35344356': 'ShinHodou', '49963207': 'Drakolian', '81582172': 'MavLow', '62251920': 'Dracorealis',
             '49172853': 'NamesWereTaken', '53358852': 'iTzNicky19', '31957989': 'Scaini', '30573267': 'Neutron',
             '44789026': 'ShiRoHawk', '91611204': '20180101', '66613184': 'HateMeCozUAintMe',
             '74349203': 'Be Careful Link', '21965542': 'UnBoundeD', '98429135': 'MVC Ryzgo', '518828': 'Smee',
             '35045804': 'Demiplane', '21987466': 'God of the Sun', '23702061': 'Mikhail Tal', '35409134': 'Srkenji',
             '25232745': 'ChaseShaco', '30366254': 'TSM Acoldolive', '581716': 'dawolfsclaw', '40272268': 'cackgod',
             '31281326': 'MaGeRdAnGeR', '77432783': 'Vincente', '66241634': 'TwTv Vchee', '36090562': 'CATification',
             '25106210': 'Daddy Panda', '74560450': 'C9 Ugly Boy', '42092205': 'Nwok', '52411380': 'TSM Curtflight',
             '22247515': 'Skirmy3', '55000405': 'Kaytwisted', '47574494': 'Kodiak4525', '29305134': 'Flinggo',
             '47381367': 'XifengSun', '34852497': 'Derp Mason', '35660630': 'DAYendD', '34101220': 'Saharsha',
             '61659525': 'Earth Bean', '36929744': 'Bartimas', '38293888': 'The Pandacreator', '80861664': 'MagicianOp',
             '53123233': 'akina speed star', '42763420': 'Frezzie', '20147952': 'Timeline', '34359241': '$rian',
             '58521677': 'Nina Bot', '31493105': 'Angeladaddy', '40111669': 'Theon Grayjoy', '95889981': 'LLLFSA',
             '25167269': 'Sunless Sea', '24216298': 'Thereian', '45839933': 'TaeSin', '61221878': 'CarrymeP1z',
             '56007546': 'Kensu', '26561893': 'Maeda AtsuGOAT', '80301228': 'Godspica', '68810248': 'Dont Snowball Me',
             '96550239': 'K 18 9 19', '35703236': 'TSM PieCakeLord', '19887289': 'Imaqtpie', '19967304': 'Shiphtur',
             '25240232': 'JordanTheBoss', '44989327': 'mancloud2', '24384103': 'Nafe', '27902842': 'A Bad Sir',
             '29535209': 'A Good Sir', '48542486': 'Party Monster', '40935930': 'In Six', '72081881': 'CYoUSSoN',
             '50612915': 'BipnChip', '46436636': 'TKE', '43519475': 'Gorseinon', '25392883': 'Roadman4Wheel',
             '72739505': 'Sole Allury L', '38694811': 'MysteryKid', '24486077': 'Kuiiko', '25367656': 'NeverFlame',
             '35603512': 'CleanupSoldier', '76400713': 'Rnbnz', '34712396': 'Big Daddy Jamal', '35445327': 'kneeb0y',
             '20939134': 'HoneydewB0ba', '35430881': 'Rancid Chaos', '47776060': 'C9 Memeos', '89160839': 'Vangy206',
             '39243255': 'Jake38', '23334519': 'Auraseph', '22767472': 'Aia', '38880052': 'The1stNPC',
             '42251981': 'Middo Kudasai', '24697706': 'RagingDonkey', '21491863': 'Viraemia', '55430130': 'chao0311',
             '99049252': 'TurkishGuy', '80070023': 'Makino', '19595221': 'Assfactor', '36798728': 'SaltySwegLord',
             '39878410': 'Erkie', '45017526': 'Spalden', '32680031': 'Tasayco', '83179246': 'Tataki',
             '29375114': 'Cedric Diggory', '54579332': 'TacoFantasy', '58639872': 'Nate Trainer',
             '36334063': 'Mercury Bee', '40723657': 'Hwang Miyoung', '78820419': 'WallNut SUIYUAN',
             '93731749': 'ShortbreadII', '23467069': 'Kaznes', '32047861': 'Bones64', '19263788': 'Failes',
             '27385362': 'thordran', '23587752': 'Magnus Gambet', '40671813': 'DotcomTheSecond', '44689583': 'Nya',
             '92892748': 'Cuty Gay Teemo', '68560353': 'chowfan1', '88932006': 'Rabbit CupTeemo',
             '64873782': 'TimeToloveu', '25163218': 'Crimson Behelit', '19433124': 'Lucky Cat',
             '52268505': 'GaussInUrAuss', '25280442': 'OogieBoogy', '46323463': 'Gakko', '26825450': 'dum sum na',
             '53314253': 'Spicy Chickeen', '36912508': 'MIT Stanley', '43607246': 'dokki121', '19189336': 'EZbakeLUVIN',
             '30065436': 'King D D D', '19931602': 'Vaze', '57550953': 'Hero Rasier', '30276667': 'mynameis36',
             '37510051': 'ImSowwiez', '25911259': 'hypersong', '46994238': 'DilI', '36010806': 'PLA yyyyEr',
             '45653362': 'Jigo jitoku', '67599816': 'Send Bitcoin', '30536795': 'phillay o phish',
             '39170044': 'yestoday', '54988175': 'Mashobiggms', '39524823': 'Melt in Summer', '35530269': 'Moute',
             '44691986': 'Ð\xa0Wave', '40967343': 'Andrew Narlock', '21899510': 'Gros Big Sapoud',
             '25850956': 'Nightblue3', '83729414': 'KuvoNA', '38286837': 'lCANTFEELMYFACE', '91329284': 'Sllfer',
             '36400685': 'WOWFlXZ', '36782900': 'Cavelery', '59114500': 'Stá©®', '40625003': 'bentline',
             '27430119': 'A Giant Dumpster', '120': 'Trê¬\xa028906884', '24612801': 'TSOL SI EMAG EHT',
             '48444269': 'Morrial203', '22356693': 'Alfabet', '99359163': 'SUPPPP PLS', '22058309': 'Zaion',
             '32942415': 'byebyekin', '25388654': 'Vortekexy', '40282656': 'Dorjan', '32680176': 'ty for win',
             '29521791': 'About 39 Goats', '19661399': 'Epic ME', '47372049': 'Axelerated', '20921013': 'Alestz',
             '36881375': 'brewcejewce', '35731400': 'Bulking365', '25040985': '3pm', '47828078': 'zetiv',
             '23413455': 'Delcatty', '48670312': 'SBG 4 the Luls', '49102117': 'Olcan', '29544262': 'Bramblestein',
             '27738038': 'Camp Me Please', '21489678': 'BrandonSanderson', '24606717': 'TheRealVeritas',
             '21177279': 'Smokebird', '66253276': 'Just a Feedlord', '43086029': 'Beebeebik', '24874120': 'Asanii',
             '35397712': 'WingCrystal', '80001096': 'FallenHomucifer', '30852028': 'Acrillex', '47742311': 'ARAM Akali',
             '73077775': 'Boom BaYa', '23040080': 'Crying', '71332234': 'zachstache', '25316304': 'BornToBeWiId',
             '40275955': 'Its Valor', '30644686': 'HohnSun CN', '51969140': 'Cidrik', '31059170': 'misayayaya',
             '87052990': 'RETNI', '24139627': 'NeverfailSC', '22428533': 'Mammamia', '24598046': 'PrinceXpKJ',
             '64847812': 'maryyjanes', '35239886': '243pieman', '70173081': 'K3nch', '60901554': 'xvinnyp',
             '84530869': 'mYvez', '31900887': 'Blaze boss', '60061207': 'Festinatio', '66359111': 'ThePerfectBronze',
             '20044918': 'D E Merry', '70189819': 'My champion no Q', '64791664': 'Fake Okito', '39488973': 'BaByZ90',
             '40734430': 'CaitlynUltiedJFK', '67175894': 'BabyInADumpster', '20174735': 'Xeon',
             '25661015': 'dog18speed', '1821': 'bigfatlp', '79902609': 'Eitel Eyes', '45410069': 'BigMagicStick',
             '68033285': 'The love Kimi J', '26439849': 'The Tilt King', '22773863': 'Vespera',
             '21362210': 'Dildo Cowboy', '40265172': 'Curranchula', '30186393': 'Les Meiko', '26348572': 'Teo05',
             '31792958': 'LittleChimp', '56302542': 'love neighbor', '44858378': 'The Viper', '38129280': 'Atrophis',
             '45129721': 'pieguy77', '84480085': 'DLT2324', '36820768': 'Songbird', '99193303': 'TSM MaxineWaters',
             '23321352': 'Afro Jhin', '26473633': 'DikuBiku', '38309905': 'Piltover Customs', '39515502': 'Visom',
             '55499502': 'NoDivingAllowed', '49102081': 'Walk With Me', '22792011': 'OZ10',
             '22792015': 'SupItsSupaStar', '71781227': 'Jelly Titan', '35684515': 'One Punch Korean',
             '93883684': 'ShiroKuma666', '50113975': 'SloppyJoe23', '39680285': 'Rikki', '21589545': 'Slimdong',
             '80269187': 'The SDF', '67649232': 'The Art of TaIon', '22558515': 'TheDestinedOne',
             '69381617': 'WT LightHead', '35795990': 'SPSxDeathKnight', '20303672': 'Automatiqpylot',
             '24162195': '76itori', '53940626': 'InflatableTofu', '95590458': 'EsmoteBurnHeal', '124701': 'Ha Zoom',
             '61281793': 'BullyHunter19', '19658069': 'Ryuutaros', '59200009': 'k1s', '35369948': 'Broseph Stylin',
             '37798470': 'AnorLondoArcher', '30619141': 'luigi2cool', '30454853': 'Saphlan', '68271219': 'Vì£¥roy',
             '30469571': 'NYer11', '38082188': 'Snow Monkeys', '28328923': 'Swedgehammer', '76833072': 'Rubasforest',
             '37252657': 'sdadasdfgjg', '32724993': 'Can You Imajhin', '72900757': 'ManKo Senpai',
             '38822154': 'Lucian top GG', '42853960': 'Mako Mankanshoku', '24221464': 'koongpar',
             '32680940': 'ShibayanRecords', '22320744': 'peyotecoy0te', '50866429': 'Hatsurei', '31827368': 'Zespar',
             '42920135': 'Schaub', '60830599': 'Brain of Carrot', '23228146': 'NoSkillsRequired',
             '30545243': 'Hunitozu', '21110262': 'Kanekiseo', '48644973': 'Heeshin', '44664326': 'sKILLSHOTz FIRED',
             '81614169': 'ARAM The Be5t', '21904370': 'Divinus', '27852692': 'Yoruha9S', '57539102': 'kn8ght',
             '90679261': 'Novel without L', '84451324': 'tractor tire', '92122053': 'TopLaner23', '86869100': 'Zelt',
             '41668518': 'Erick Dota', '41745040': 'Competition9', '40017716': 'Choisix', '75649166': 'Hanabi69',
             '45826619': 'Wee G', '20463386': 'Pikabunz', '45485066': 'Bowser257', '19903923': 'ah man u got me',
             '76289851': 'Ronnie Pickering', '92141284': 'Lucarus Ivoric', '43879966': 'The Catmancer',
             '21445778': 'inu', '42149985': 'SlendishMan', '35690742': 'banAnatz', '34275602': 'PandasButt',
             '21499529': 'BagelCreamCheese', '24798264': 'TotalSnarf', '42727588': 'WindyTrees',
             '50593191': 'Huneybadge', '38770690': 'EZclap my lane', '58231068': 'doneg00fed',
             '68989590': 'Legendary Elvis', '37143413': 'Caceres', '49680086': 'Messaiyan', '39980499': 'porousmfer',
             '70199380': 'Mattg', '99349225': 'CenterT', '51099453': 'Best Kayle Salad', '68731719': 'Snuffles Smith',
             '66899805': 'Jealous boy', '37988527': 'Reminiscing', '80370362': 'Kyiabluee',
             '34912667': 'Dinosaurus rekts', '42119443': 'ZLJGentleman', '51148241': 'Kyyazzy',
             '50682664': 'MrGangPlank Bot', '32681855': 'New Bee OR', '24832712': 'All Good Things',
             '24227106': 'Lucaslord', '90580627': 'MaySuNN', '32490445': 'What Mini Map', '31077227': 'Telz',
             '39845524': 'Mack978', '24277780': 'Too Asian Bro', '20133808': 'Cannolis', '35371710': 'BadKidDestroyer3',
             '40574524': 'Lnsx', '49378066': 'GET ZONED', '23792451': 'JustFalseX', '79699368': 'RabidCactus',
             '33111534': 'qu1k', '23245665': 'Scrandor', '21490433': 'goldenglue', '43155210': 'That Guy David',
             '39825307': 'Orinj Ocean', '45776727': 'xslugger3', '67050785': 'Nerans', '49292855': 'lighting987a',
             '49182419': 'Yettes', '94199087': 'ShiningUnicorn', '71189157': 'Alucardzz', '23418972': 'Cuz Walk',
             '28420653': 'Aggrbargl', '37988556': 'Kelcey', '40975024': 'Domin8rDutt', '24306886': 'Steven Xiao',
             '68259686': 'Voreign', '98470376': 'Wyisleaguetrash', '45677032': 'Mr Quopple', '60686976': 'MoodyMan',
             '44082781': 'jafajkdgfjkasdhj', '19615506': 'FJLM', '24822862': 'Topopotamus', '21978289': 'yeo1',
             '23573965': 'Blademanzen', '37462379': 'ArgentumSky', '49389151': 'Bî³¨op', '89490780': 'Sherry ice',
             '36832273': 'Rip901', '72139492': 'll Dracarys ll', '44208150': 'U Shall Not Kass',
             '59502404': 'Blankless', '45304701': 'Wanta', '80489555': 'UB saozhu', '39993483': 'Mosby',
             '22714795': 'Cjohnpark', '83053116': 'Captain voyaja', '22737722': 'Tymer', '53016284': 'cheba dan',
             '24263274': 'FruitPunchLord', '71052126': 'mingzikeyi', '29219483': 'Equality', '47210618': 'Mr73er',
             '27962303': 'Kelveaux', '21113761': 'Saeith', '70413366': 'USC Tanknstein', '37501171': 'Unloaded',
             '24854065': 'Keener19', '72801112': 'i am not old', '39805214': 'ANG3LUS MORT1S', '25421302': 'Robotdroid',
             '72310360': 'Desire Is A Sin', '39532278': 'jNoblessj', '67070363': 'Teddy alwaysRUT',
             '32989316': 'pooky57', '32947921': 'SpookyBoogie8', '28530150': 'Extreme Person', '35749596': 'Filoplume',
             '58870068': 'PunOko', '75900909': 'Ne', '19770082': 'Cris2', '27816311': 'Don Tito', '30204038': 'Deka',
             '37288239': 'Ravenharts', '50240003': 'Fused', '20739331': 'White', '83499566': 'LostTokyo',
             '51810366': 'Kcats', '28009735': 'Jiminy Crick3t', '51402027': 'Cemonic', '64560440': 'Best ATM XD',
             '19230700': 'Feden', '36635577': 'melonstick', '31546636': 'Intent1onal F33d', '98779183': 'MySheng',
             '21093289': 'pwn n bwn', '24678882': 'arenu', '50251928': 'Fate Space', '24818847': 'Redulant',
             '24825994': 'Jesse Wayland', '36771345': 'SSSSe', '42067695': 'drummaestro', '31939393': 'Shalgiel',
             '40383947': 'Hugemushroom', '63680476': 'Littlemushroom', '57392045': 'Carla Yeager', '22527616': 'ikoru',
             '21416149': 'Follow my TikTok', '72322250': 'cinamonrollz', '32843340': 'Daniel9981',
             '28810916': 'Immolating Pyro', '32170462': 'Epiq', '40719715': 'This Is Celery', '67800992': 'Kris Skys',
             '32804035': 'WolfyKinZ', '66722022': '4sh Ketchup', '30260694': 'SloppyMcFlopy', '31906553': 'Xehnam',
             '45795786': 'Veiv', '62250480': 'pls win coinflip', '39574816': 'Pâ²´y', '77779176': 'Santorin',
             '29362306': 'Mizt', '87230278': 'Not2Clean', '98019882': 'jkHKlgOHWGHAOHGG', '84190816': 'Fat Smurferer',
             '71129445': 'xScruffers', '35593768': 'Juked', '50939504': '4876', '39015814': 'Sylvestar',
             '526184': 'Big Platypus', '30054717': 'Poppys Hammer', '21098444': 'Autolykus', '31274923': 'Lovefury',
             '21199585': 'Yzu', '53943570': 'paradiddle4', '30442981': 'Celomius', '31535950': 'Lord Artorias',
             '66429340': 'Deep Banana', '27680597': 'MasterChipotle', '24417086': 'Ayaria', '32209400': 'Noicest',
             '34283703': 'DonaId Dump', '31243372': 'Dunkeaon', '32844091': 'DrunkCatalyst', '21564449': 'Wun Six',
             '32744499': 'thicc af', '70699300': 'KamenRider Snipe', '21511974': 'XxxChris310xxX',
             '38132000': 'Hamburgirl', '24894847': 'Yaniqueque', '24641780': 'Vietnam IIl', '29220089': 'Atrous',
             '58415580': 'A Grumpy Throne', '40355025': 'BBQ of Justice', '54432025': '6025', '75740608': 'Extorcs',
             '71459269': 'Audi Rs7', '25887751': 'i am neal', '79529942': 'Lamie', '19079393': 'Garani',
             '71402604': 'SevenAster', '35499513': 'Jim Cantore', '48669192': 'AK47 JacksDaddy', '34552015': 'gg wtf',
             '25756588': 'Rove', '34764162': 'Chrono Resonance', '76892421': 'Faabuloso', '34038225': 'The Spanking',
             '40353968': 'BrownDigga', '77479206': 'Villaintina', '21021666': 'azneric', '78443246': 'JasonHu5471',
             '41242899': 'RunawayBaddie', '32929410': 'Zxyc', '41883371': 'mixmaster', '35463846': 'foopdog11',
             '84691415': 'FaZe Swag911', '76950959': 'shyy ahri', '87920123': 'NA OrphanN',
             '91581116': 'G U E R N M S L', '74822664': 'Enz0MeH', '44278296': 'Zalt999', '24348896': 'bazerkaX',
             '50187263': 'Gigii', '93731255': 'dsazfxgchn', '19647481': 'Rathma', '22654107': 'yhw',
             '71899217': 'Anivia Kid', '28336979': 'Icipher', '51786517': 'Saikhan', '25225816': 'MetaSupport',
             '84019131': 'Hashmalin', '19141243': 'AstronautPanda', '25161762': 'Final Flantasy',
             '89099316': 'NarcissusY9', '85869139': 'Tokeins', '23851592': 'RSB', '19620907': 'Arsi',
             '64619238': 'i play hunter', '24131245': 'A Speedrunner', '32412738': 'tankbomb25', '30311270': 'Portray',
             '23923979': 'Brigade', '22878439': 'Khoh', '29100338': 'JustAwayz', '39267240': 'chessmage',
             '22928399': 'Zumanzo', '43257123': 'Feed Sin', '36659953': 'nolol456', '53317051': 'kkid',
             '51082038': 'Riven Miao DA', '90783774': 'SelfCaree', '30314638': 'DarkWingsForSale',
             '27332688': 'FOOTNOTE', '69549389': 'becoily', '21390175': 'Branch of Fate', '22670229': 'Shout',
             '35850178': 'Mascot 3000', '28993282': 'filedoesnotexist', '26763392': 'Graxter', '26266825': 'Acquiredl',
             '48448225': 'whosyourdaddy214', '24361972': 'Twitch Chat', '95850807': 'Sherane',
             '59678262': 'Sylvia Mani', '40939286': 'Master Dwarf Bob', '26810236': 'Vaehar', '32263267': 'yippity',
             '84899573': 'psp', '36463278': 'capitaI D colon', '73380041': 'Essika', '42173032': 'Neverwins0',
             '63452023': 'Shielrin', '20964975': 'Not a Neko', '89231945': 'ozkai47461', '91615420': 'KatEvolved',
             '36111109': 'Julien', '21103810': 'Andybendy', '99459101': 'Kooonzi', '81724004': 'seekersi',
             '88163291': 'M0g1cian', '33121687': 'eVictus', '24427958': 'Gandalftheghey', '19809674': 'RDX',
             '35184105': 'hunterjoel', '38610015': 'Pancake is good', '28890612': 'oblongBanana',
             '23271105': 'GOAT LEBRON', '81600898': 'preson1', '47359161': 'Warren Liszt', '49134139': 'FM925',
             '60232386': 'Magicani Master', '52849565': 'Awry', '50554200': 'LUMENNeunteTiara',
             '56049630': 'Sticky Hands', '38269443': 'choar', '35489961': 'ImaUs Marine', '59629227': 'Go Pix',
             '24763884': 'Geoprow', '25276686': 'AbusedTaco', '26103607': 'C Yiliang', '76641046': 'Dunqq',
             '45970070': 'Langan', '39886956': 'Goodforlife', '49430009': 'Inkosi Cornelius', '30781298': 'Jaaylee',
             '83990710': 'Phaszer', '80329955': 'SolDier7766', '65500557': 'ZGYXRAT', '36334894': 'Flluxi',
             '20816121': 'BaconGas', '20227573': 'BukZacH', '21172589': 'Call Lin', '77269277': 'V1per1',
             '49114502': 'Octagon', '23476283': 'EricZYang', '19986595': 'LegendaryJosh', '28397433': 'Eatfood',
             '91322816': 'flatball28', '37056988': 'dclay', '68411427': 'Wizikz', '89501740': 'CpryusJr',
             '45899896': 'lllIIIlIlIllIlIl', '24780453': 'Binto', '45538066': 'BuddyB33', '62292357': 'MakinDuhBacon',
             '36731480': 'Clones R Dragon', '36754282': 'Blankcc', '55367184': 'Suuran', '81069964': 'Curtain call Art',
             '29516143': 'Freebird5678', '26366304': 'Bâ£« To Paradise', '65360961': 'Oiwa', '45582337': 'I love her',
             '40888895': 'Capische', '83531894': 'Sevenkillerbobs', '385760': 'Retrocup', '52825122': 'Chomo Jelly',
             '79920062': 'Mad PCer', '65729809': 'KalyaLily', '21381148': 'Kangsta', '36189289': 'Mr SoloShowChen',
             '19831923': 'Mò\xad³\xa0', '58089141': 'gimme gum', '36365191': 'Yabal', '37773439': 'code 9527',
             '47904698': 'Ng uong', '87381461': 'Hiatus Universe', '28911306': 'Gametophyte', '89090715': 'BBQfromCHi',
             '70649855': 'CPTN BrinnyFunny', '31477644': 'TheOddDucky', '63939664': 'go learn',
             '55502923': 'DiskoBiscuit', '22775683': 'Zero Pressure xD', '92639804': 'LAN Feng',
             '39876431': 'Majestic03', '60012275': 'Amber Is Mine', '87439213': 'ì®¯ri', '28437579': 'LikeAMaws',
             '61749455': 'BBBiuBiuBoom', '30262167': 'xRiki', '35901786': 'Grab or AFK', '212955': 'assasin313',
             '75084187': 'Skoeo', '20495845': 'MustBeTheGanja', '21983715': 'Nazruk', '54900245': 'Haijacker',
             '59265041': 'Poo to the LOO', '31910330': 'Lunarwalker', '53091522': 'Hoseki Morganite',
             '24716782': 'Gone', '42686293': 'Catslive', '22141445': 'SandPaperX', '23890102': 'YoItsK',
             '45186258': 'lc0nic', '20821665': 'Hardo', '24988249': 'EndlessSlawter', '44206228': 'RunningAtom',
             '77289398': 'Syncrokill', '26591530': 'Wark', '79682749': 'wsdk54fjskj3', '21234494': 'Crimson Rising',
             '24556014': 'DntStopBLeeVayne', '24340057': 'Unruly King', '26413564': 'a cute dragon',
             '46292286': 'Zonked', '69280664': 'MAGODO', '5724': 'Foggles', '79812625': 'SB TENCENT',
             '51405778': 'Zibi Support', '44330436': 'Devalois', '49241838': 'Orange Tempest',
             '19839806': 'blaberfish2', '35610675': 'TyChee', '33441071': 'IchuckYOnorris',
             '27251616': 'ULookSoCharming', '83631734': 'DaRkHaWk72', '92940479': 'Want To Mess', '35709967': 'skluffy',
             '42209599': 'Xtr3m3soul', '39576450': 'AlbinoSable', '79460768': 'YongeBoy', '50791972': 'DR0G8A',
             '40665927': 'Moo is my master', '40725925': 'Bark Uh', '24908632': 'Hycl', '57466470': 'Jon Footpenis',
             '40279354': 'Mango Lollipop', '74949119': 'ButtermilkRoad', '29312001': 'Die for Kills',
             '35275298': 'Sweet Baby Rizzo', '92110594': 'Bottery Parn', '20826814': 'whatahuli', '22512055': 'Derque',
             '37876796': 'ZouXing', '37450943': 'Shuai BuGuo 3sec', '90662598': 'Nohoko', '37064515': 'Aarron',
             '27954118': 'Ravens Equinox', '34825320': 'doorbell96', '34600127': 'Hi Im Procow',
             '40790787': 'Cutest Timo NA', '31891334': 'Zipopotamus', '21242597': 'samart',
             '39637538': 'EnigmaticResolve', '70481142': 'MyTeam BotTroll', '35717386': 'OverRice',
             '88531411': 'Johnson Wang Pig', '44699406': 'DA WHOLE PACKAGE', '26094905': 'Ceramic Dildo',
             '30109768': 'Chaotic Clouds', '93240670': 'Hyooon', '45538147': 'Whoppers', '31560988': 'CaitlynxGender',
             '28962728': 'Tchikou', '39040566': 'GGS Matt', '87759312': 'lkuya', '31233054': 'THE Jons',
             '76912916': 'Rose Queen', '31326317': 'tsparkman2010', '69814025': 'ForeverMidKing',
             '44725874': 'TiddleTaddel', '31492786': 'A Real Weapon', '36391234': 'Call Me Zac',
             '44103593': 'SsipSunbee', '34599456': 'XAquaKnightX', '67561035': 'Mewko', '50033093': 'Baddest Hooker',
             '30692681': 'Supreme Nipples', '21026030': 'IO ADO D', '23683386': 'Noriala', '44154581': 'Jannefalopez',
             '50479201': 'Younglister', '25803275': 'IdiotLostOnPatrl', '33341541': 'Tortuganator',
             '40920065': 'Pepperidge Patch', '45598201': 'Hi im Freeze', '35415473': 'Yamï¿½ze',
             '21224186': 'Chicken LittIe', '30307001': 'Turc', '51409229': 'MADK1NG', '93529573': 'midIane hokage',
             '94229927': 'Aspect02', '56985923': 'bling blaww', '41866227': 'F is for Faker', '28420020': 'Makake',
             '24858900': 'AceWindstorm', '45300308': 'Yá\xad¡', '21847981': 'Suntail', '37798900': 'Tesla Motors',
             '41312306': '25th Sol', '24149379': 'Riggle', '35510614': 'InADyes', '19576991': 'My Last Surprise',
             '22136541': 'Dalrix', '23749688': 'SkieLok', '22264212': 'Eat Sleep Hunt', '19852981': 'I Am Ronny',
             '56139405': 'WhisperInMyEar', '153': 'ÕµÕ¬ 59811860', '22378210': 'Yushio', '24211458': 'lijojo',
             '66965848': 'Waffleosophy', '39309359': 'qwpkxc', '34517011': 'ItzMutie', '60156847': 'sly1ryan',
             '34890772': 'Shtand', '97880345': 'tarzaned5', '79811449': 'IG TThe Shy', '25796026': 'Dreadnaught',
             '60833704': 'BlowB Daddy', '32836769': 'jrrules', '34911482': 'Ajbsox', '58992097': 'NicholasYZ',
             '47901212': 'Organized Fridge', '24893416': 'Crusable', '43962508': 'ou dude07', '57310779': 'EricTamaru',
             '30608978': 'KWB The Jhinius', '92749138': 'LuciusRex', '72670127': 'Vine715',
             '60022191': 'scooter mcdooter', '19573196': 'Kargarok', '20039439': 'Txengyee', '30453140': 'Izanani',
             '44203317': 'grandmaster127', '25152817': 'SEH Pandorum', '21448695': 'XandP', '88891947': 'US Danny',
             '37935750': 'Abominate', '39945299': 'Lolinomicon', '99200657': 'LLbbPig', '70231643': 'Whered Fk R U',
             '66740296': 'G1ao', '35322061': 'iTzSemantic', '22713009': 'Bewear', '46332533': 'tipsygelding',
             '45025810': 'Specz', '20235955': 'an norelco advtg', '42826355': 'Kyprios', '27412892': 'Strange Mango',
             '52211582': 'Alistar Hero', '40397116': 'Psion Flayer', '66845166': 'RuinedKingJAX', '22258477': 'Gencyde',
             '24037320': 'BIoodySky', '26430615': 'DarkBeast Paarl', '41646368': 'DiIIards', '44856473': 'Demosina',
             '38624158': 'Foxprince39', '32857627': 'Akiyuki', '40170552': 'chuggingwindex',
             '24799163': 'Tactical Meme', '50371928': 'Big Guwap 1017', '71021570': 'IamButterBoi',
             '40356892': 'GUARDAD0', '24272097': 'pewfie', '20094827': 'Imnotmad', '46178658': 'Discoverably',
             '72589443': 'Iapetus', '25278759': 'Quagsires', '74741940': 'SquinchyJesus', '30822239': 'Mr Only',
             '57089890': 'Change It Up', '31892374': 'Ye Olde Timothy', '98853002': 'Do u like fish',
             '32299406': 'Spawwwwn', '25005620': 'Mcbaze', '43173587': 'Herson', '35460596': 'Polyxenna',
             '52415539': 'Hajib McRobinson', '24615190': 'Chef Rycan', '88750320': 'LHX2403', '24600559': 'Freetorule',
             '83861005': 'zuby plz', '92029712': 'KingRaptor724', '39935161': 'KasokuSekai',
             '30037826': 'Gooey Panties', '36091354': 'NO 1 CLL CN', '79681195': 'Catastrophe4U', '83430267': 'NMBiss',
             '51372095': 'AcidRizzle', '37790021': 'Rock Bogard', '78652687': 'Shsiiske', '28912077': 'WiIdish',
             '20073484': 'SpillingStar', '34726166': 'IBBolin', '54421811': 'Ë¸ee', '30873700': 'IOI yeongwonhi',
             '97380956': 'Hi WiII', '42959737': 'Ketsueka', '22448386': 'Netorare KING', '47989467': 'OhShootMan',
             '19582548': 'Doc Chì£«en', '30365288': 'BarrackiBombYa', '36465687': 'Computer', '22622810': 'DraxtR',
             '68319551': 'ColmtheThief', '43690919': 'P1atypus', '20918669': 'elise player',
             '47509064': 'IAmThrackerzod', '55884312': 'IBangMidgets', '23156602': 'LotteryApple',
             '22584707': 'Apathia', '20665366': 'Micah Burleson', '59326950': 'Q2tec', '31372381': 'EREPYON',
             '41950889': 'Luckeren', '43381059': 'Soulcrash', '306463': 'Get Derived', '46360333': 'iampatwalk',
             '45084341': 'Taeyang SoI', '34022582': 'AIrighty', '20832987': 'Xelltrix', '50362215': 'CowsGoMuu',
             '25439101': 'Mutes', '74289119': 'FarhanX', '52559520': 'Tony Top 2', '29161654': 'mulgokizary',
             '61542283': 'huhi', '47943093': '3in1warrior', '35571306': 'Prymari', '19738326': 'Darshan',
             '72952897': 'wudiadc', '20849995': 'xChurch', '40718357': 'rcrsvs', '44227250': 'myoung2613',
             '44153012': 'McDull', '49351377': 'Mantus', '51006247': 'The Betraitor', '22022473': 'chokingteddy',
             '27741987': 'Battousa117', '30315744': 'Ç¯balt', '22907588': 'Hatin', '47504968': 'Teshub',
             '81189179': 'DarthnEvade her', '68510592': 'Astral Crusader', '24415732': 'SalvoPark',
             '46114318': 'Spirits Rise', '51373615': 'Booty Savage', '34082527': 'Mioyle', '53812378': 'seymourwiener',
             '39680074': 'RevUpThoseFryers', '32178289': 'Qualified Ape', '31204046': 'Seoulman',
             '41256247': 'StormbIessed', '27291302': 'Twtv Hanjarolol', '41213210': 'DrewDozer',
             '76833348': 'need focus', '94561198': 'GGS Mango', '28551032': 'Kellatha', '54945532': 'WasianWoo',
             '20502717': 'Ditpwn', '93920073': 'Ciaoe', '47852131': 'Pikipek', '21981953': 'Stand Up Kid',
             '38973461': 'MagikMak', '38243736': 'Sî¯®ara', '39585223': 'Bacon Bot', '42043299': 'Lionhead',
             '50552531': 'Wretched Unicorn', '56512821': 'braindead moron', '32530945': 'Bangkok Ready',
             '24860356': 'Hir', '46561332': 'SKT T1 å«¥r', '70073684': 'Scrub64', '91677725': 'Angé¬\xa0Maker',
             '20016129': 'lnsideMeOniichan', '20181337': 'PhenomEX', '63291': 'Sunset', '99280530': 'lIIIlllIlIIlI',
             '48647860': 'RacistSeaTurtle', '21501967': 'Give Me Ur Legs', '97362763': 'Shiba lnu',
             '20823651': 'Smoothie', '36541197': 'Repfix', '22785204': 'Wingthree', '23351769': 'Aionas',
             '80942397': 'StealthyF0x', '39181251': 'Igtenes', '36259205': 'im dumbass', '44716470': 'NecroCola',
             '39819517': 'rochester girl', '26091857': 'memory cards', '22178345': 'Hugguy',
             '40720499': 'Afroninja Guy', '52352930': 'Kushukh', '29713621': 'Zlaska', '23172762': 'Unhewn',
             '42932210': 'toxicbeans', '43831214': 'nakallama', '166586': 'Revenancer', '23365226': 'Genera',
             '38951410': 'CASBUBULIU', '47627895': 'Only Carry Girls', '19531449': 'HeadBox', '23646048': 'VahaLa8',
             '27039630': 'Zackary Diamante', '36100051': 'Twtv DirtyMobs', '34983603': 'Licorice',
             '38809624': 'Sophist Sage', '28640725': 'FrozenNight', '21697259': 'Aielth', '19199530': 'Xpecial',
             '39459832': 'Shafiq', '19061980': 'Lourlo', '19320840': 'Chokezilla', '21766551': 'Rivian',
             '34103239': 'FinaI Solution', '37812016': 'p9hatvo2tsg5y', '42959195': 'GuardianzForce',
             '60297540': 'Yves Ice', '96360419': 'bootyfIu', '31891346': 'I Want Doggo', '50208688': 'TC porsche',
             '39866447': 'Mid Bot', '60031276': 'Lingy1 Siren', '59849109': 'IG ChamPion1', '31043122': 'Jintea',
             '72490184': 'SplatterJay', '22226348': 'Doffie', '42028165': 'Chatty Poppins', '70521697': 'Maxiiiiiii',
             '35696243': 'Doonagoowin', '442232': 'aphromoo', '77491374': 'Gio Monster', '22525768': 'ZapDDoS',
             '19542853': 'fluxable', '75231117': 'Jotunheim', '22192687': 'Gweiss', '49290152': 'TURBO SCRIPT',
             '20534978': 'FiveofSpades', '21861110': 'TyÌ¥r', '538052': 'LoveOfNacho', '32208093': 'SneakyStevan',
             '43683910': 'Hpseven', '50193621': 'SuperMacho', '37334747': 'Brovich', '20688264': 'HerBF',
             '50126741': 'Hypper', '30553476': 'improve my brain', '66929247': 'Joeyyy', '96899278': 'Taxatï¿½lsTheft',
             '60469878': 'Nice play BRAH', '71569457': 'Darkness Dude', '38242611': 'SideFlanker',
             '21263184': 'HayabusaRyuji', '28963857': 'DownsideUp', '28437705': 'Doomseidzarro',
             '47743187': 'MagikLift', '31856904': 'Eason Cyan', '31335652': 'DrTrafalgarLaw',
             '24198026': 'cucklordFLEX', '23659854': 'Erza ScarIet', '20615392': 'GhostFlake',
             '51420451': 'Your New Stepmom', '87180769': 'second walk', '20506621': 'Doctor Tape',
             '34702407': 'yslicia', '34196626': 'StopAction', '44257432': 'Troll ControI',
             '21789825': 'Feed on purpose', '69332104': 'a Saleana', '354214': 'Moonstarr', '20604419': 'mvsrocks1',
             '31746401': 'NaabinDirty', '34109001': 'Hatrioz', '58465778': 'Quoxide', '71341633': 'Pajama Teemo',
             '48652916': 'Erazer', '99299551': '86184133', '74259211': 'Doflamingo2333', '213726': 'devops',
             '42782462': 'Master Baner', '62343730': 'Whatnos', '47578742': 'JamNToast', '20718525': 'teeheelemons',
             '24820173': 'ugettingganked', '21416360': 'iChasedYou', '282481': 'Unitedsoul', '25001584': 'Newinuyasha5',
             '70300055': 'Swife101', '37354134': 'Since', '58772962': 'FriggenCrazy', '76981748': 'exocel',
             '26412149': 'Stunned', '20972149': 'Genryusai', '20830513': 'Ghyr', '51432074': 'Raid Boss Morde',
             '23481588': 'Dakimakura', '23343693': 'AmateurEx', '32196972': 'ostinwitz', '22614082': 'Ch33',
             '38899215': 'Oceanman93', '31984700': 'Opposited', '23127751': 'Piece', '19724994': 'Wood',
             '20786792': 'JesterSummoner', '48119638': 'Chicken B', '25223292': 'ChaosFire55', '69482545': 'Keebler 9',
             '59653504': 'Kinder', '62250509': 'SamMsln', '47360446': 'Fellafawaffle', '24427535': 'Ansem571',
             '50658921': 'Peachsicles', '45560819': 'Bake a Bagel', '19068189': 'Slappy Nuts', '35263972': 'Dragovoid',
             '20589413': 'EpicBioHazard', '47122563': 'DeathBlaze0', '71409555': 'Vehtra', '22528705': 'iFearless',
             '20187086': 'É´ienne', '48241365': 'Dr Challenjour', '26677986': 'Frunfru', '29460500': 'MyLeftTestee',
             '59101521': 'II Sneh II', '68019263': 'Lvl 35 Magikarp', '21118846': 'EnergySurge',
             '24842879': 'LookAtMeNovv', '60939398': 'FenixXx', '74612731': 'racecar3112', '30654418': 'odnes',
             '38299680': 'phorate', '28599110': 'Pingemu', '19911057': 'MaxtheShady', '23611178': 'Fanyful',
             '21556685': 'The Buk Lau', '46074467': 'pure cocaine', '79791134': 'Isolateswww', '34022121': 'zlsyerc',
             '29213545': 'Edric', '25640878': 'Heso', '34739222': 'senior evil', '36970037': 'Aqwerty',
             '36751235': 'BieWenWenJiuSong', '34540290': 'VAJAJA', '34047899': 'RubyXiaoLong', '30623585': 'Climate',
             '52326216': 'outback romanium', '40220617': 'Subduction Zone', '20082683': 'Quantum Fizzics',
             '83629091': 'Swifte2', '44180683': 'kiface', '39654184': 'godzilla brain', '24611988': 'KrakenAyy',
             '93722241': 'Rahnnn', '24421759': 'SkullKraken', '47065205': 'Sakia', '36376874': 'x GreeZy',
             '22923847': 'Gin and What', '53361153': 'RoosterRooo', '22340236': 'DahnStar',
             '20665605': 'Kojirï¿½ï¿½aki', '19811661': 'eeK', '40366313': 'MercwithaSmirk', '40892363': 'CainMakenshi',
             '483469': 'bubby boy', '19360602': 'Kazake', '43249997': 'Ganked by a bear', '22867843': 'Sarif Fice',
             '27183868': 'Beast Machine', '44810275': 'yummybluewaffle', '25844953': 'MidnightTacoRun',
             '43234915': 'ICalledFillFirst', '20004694': 'Afteg', '30658156': 'IlllIlIIIIlIlllI', '20256768': 'Xizoy',
             '22979188': 'Scarlemm', '77299178': 'sionainnn', '22033628': 'Eldrii', '39628859': 'Nott Creative',
             '147322': 'Narvo', '67001104': 'omggiraffes', '76072453': 'Hi Im Citrus', '21734763': 'ThisMuchHPLeft',
             '31156639': 'Nameless Youkai', '32897515': 'kikachu', '35651923': 'swiftlee', '31607198': 'LampShayde',
             '64962559': 'Shinpakusuu', '49223216': 'a900017', '58423297': 'a very lazy cat', '20806885': 'Redgaze',
             '51269266': 'Juansanity', '25169634': 'Gomabneyo', '36020065': 'Zekt0', '48540138': 'Nicholas Zhao4',
             '39801309': 'Benjamin Liuneng', '20580788': 'Elmoo', '49323573': 'Aarcus', '58543782': 'megalith',
             '21947759': 'PainPal', '38385920': 'TrampledByWeed', '36959949': 'Serasae', '37042941': 'Fallnhobo',
             '30036211': 'Avacod', '21152920': 'Not See Germany', '21214027': 'Shawner', '59833159': 'BastionsHollow',
             '31010904': 'AngryCritic', '59829422': 'Philosophery', '38070302': 'Stá¬·art', '39812045': 'CastleSmasher',
             '39208311': 'Dnitro', '26702846': 'DeftPunky', '24090489': 'ego brain', '30779352': 'sh4pa',
             '35200912': 'Duxregni', '21133544': 'Jeem', '50877721': 'Doubtfull', '88229545': 'Gate',
             '37979177': 'Mooshn', '29306588': 'Northwestern kid', '25220664': 'Trail Mixed', '24185732': 'Toastur',
             '37379052': 'Fylps', '62344852': 'BrutalJk', '69993427': 'AK47 Alice', '72332514': 'TriHard',
             '43779756': 'HashtagThatPower', '51774253': 'TitanBoss', '60801411': 'maximum tryhard', '25348510': 'Muzy',
             '60322930': 'neukda3', '20056332': 'Lerky', '21092237': 'Screamer', '19647249': 'Magepower',
             '34383884': 'Korean nmsl', '39652656': 'Dr SonicWave', '38271429': 'Potato Boat', '34903601': 'marktobar2',
             '43978164': 'LaBron', '24910677': 'ThePrinceBlue', '21233089': 'seeleyy', '59429678': 'Fulgurite',
             '24452827': 'Ventrious', '41926290': 'Herald 0f Death', '70253369': 'Hiep Nguyen 01',
             '48247129': 'Wrecktuum', '23351099': 'IRainl', '23835975': '4znNool3', '30628197': 'Blkrapids',
             '46404768': 'MasterChop', '45680451': 'Prince Grimm', '47788083': 'DEE Fault', '22234637': 'jambes',
             '20611031': 'An Obese Panda', '21202019': '5fire', '30580841': 'Oriku', '29762385': 'phatDiesel',
             '19582043': 'Zeirk', '35641848': 'Xerus', '56917806': 'HM21 Tower Dive', '89919127': 'Moyyee',
             '64910037': 'Penguinly', '65031800': 'LionKingKaillon', '26272803': 'NCnotorious', '34271115': 'CG Il',
             '23777189': 'phanDAR', '74359090': 'HiImCorbin', '43470614': 'Calabera', '29442901': 'Braindead Dad',
             '23658020': 'Deathreel', '38288518': 'I dont Smoke', '24195679': 'Osaml', '60409544': 'shadow25605',
             '34813823': 'Squash Banana', '70412492': 'k2523', '48617110': 'th eggsalad', '40835255': 'fà¬¬',
             '77750220': 'BloodWaterr', '24147252': 'Shin Chin', '19883321': 'Euphemisms',
             '47795841': 'TryhardVegetable', '43856492': 'honeygreen', '39410040': 'Hoiyuen', '31104041': 'ProEnough',
             '81132742': 'I B', '39887992': 'Trung39', '32158564': 'Helping', '35564624': 'UW Deng Zi Qi',
             '35021629': 'Vayzian', '22823521': 'Lolmart', '22923694': 'TheKoreanKappa', '23133946': 'Redrosid999',
             '22540545': 'Cereal Life', '21124209': 'HuaZero', '37420176': 'Sherman70', '31563998': 'germr1',
             '55828610': 'IllIIlIIlIIllI', '63449231': 'Big Pepsi', '25093663': 'limezest', '44107594': 'Mr 1in',
             '20122678': 'Grumush', '94790456': '3SecondRoot', '48136933': 'Grae Clementine',
             '23690707': 'Galatea Prime', '38690179': 'LostOne045', '20172733': 'iTickleYerPickle',
             '22655756': 'Call Me Khal', '25892948': 'ChiHoSong', '65570693': 'CrazyCFH', '47717331': 'Commando Cookie',
             '65363179': 'MrBojanglesx', '44499448': 'Abrams', '91452125': '1800 Gà®«AHoe', '68139466': 'Anemoiskye',
             '23261421': 'Otrev', '36531348': 'VUA', '23677421': 'Croc Hungry', '32153703': 'Humble Jones',
             '376421': 'JGrave', '28880632': 'Abss', '83133199': 'IcyKnight1', '83750505': 'Lewis is GOD',
             '20066844': 'ZyniX', '49208816': 'Thalies', '55629820': 'Butler Delta', '69342970': 'Hestory',
             '29803385': '88key', '43692833': 'OhMaKami', '39090903': 'CaptainUsername', '22062878': 'Unhindered',
             '43541296': 'Derpanator115', '20733100': 'GoldenWarlord', '69432007': 'Butnek kid', '48626806': 'ileadz',
             '26289480': 'Flamboozle', '21533287': 'Super Reformed', '22009308': 'CrAsHBiTs', '34525479': 'Aureou',
             '62310049': 'pa81382', '23541463': 'Dante Highwind', '37330206': 'Sir Patty', '22519110': 'F53710',
             '34972007': 'Cile', '22447403': 'PrismaI', '35097344': 'duoking1', '98500608': 'Hental sensei',
             '31331497': 'LikeAnEmployer', '25443426': 'michael2001', '24738057': 'Rain Shad0w', '38796703': '12cz',
             '23615523': 'iFaqu is SPED', '34291816': 'animekay10', '51782180': 'Eric Fartman',
             '22247978': 'Friendship', '19148891': 'no fIow', '26262985': 'O Face', '59654137': 'C D',
             '45639915': 'ChazGoRawr', '32709873': 'suprise motherfk', '37295395': 'Empty Allen', '19614677': 'Anchan',
             '66685054': 'GreenTeaXMaster', '92462046': 'BrawlBallie', '35592560': 'DEMOCRAT TRASH',
             '36960890': 'dog toilet4', '24188054': 'BarbequeQ', '89390739': 'Gabrielle4ever', '18983679': 'PewPewQQ',
             '62051206': 'Bradoa', '69983485': 'lG BaoIan', '91393436': 'xUiMiranda', '38235119': 'Noah Is Bae',
             '23762633': 'Lunarly', '44800037': 'Disoriented Emu', '70439864': 'smashed brains',
             '31167503': 'Koneko314', '44479272': 'will win', '25199530': 'BobTheMoon', '91498125': 'inteIligent',
             '40841925': 'BlueRageMage', '45365699': 'Faery', '71701907': 'WayoftheWanderer', '76071366': 'NKDA',
             '33390926': 'Lai', '32897297': 'pwnagenerd13', '40822576': 'Maroon Turtle', '40256203': 'KserScrubLord21',
             '68091415': 'Waifu ga Shinda', '45473669': 'Lord Hueington', '93190616': 'Vivid Sun Leona',
             '31104582': 'Thenotsocoolkid', '31043614': 'Loiterer', '31114744': 'BreadIsGreat',
             '33289184': 'Corruptgargoyle', '40820946': 'Naru', '66512063': 'HI Inori IMY', '21673348': 'Bang Seulgi',
             '23956153': 'Snack Bear', '42798997': 'TeaVirus', '37248526': 'Dokkaeebi', '55961449': 'Defender41',
             '67014446': 'Kimchi Krusader', '48710328': 'Animeology', '47624437': 'nauy', '35315365': 'Rival Jd',
             '46299702': 'HVN', '65733612': 'Kya Kitty', '58732493': 'Grayfang', '47339861': 'Miss SilverFrost',
             '44369509': 'Rodi', '32907326': 'GankedByNausea', '69921820': 'TrueSerendipity', '86160599': 'OGNachoBowl',
             '20302923': 'Lvl 99 Kenny', '37106639': 'Im Ornny', '49004522': 'Namirie', '58607541': 'Robbied432',
             '34752202': 'TastyMidget', '43562864': 'IDNATSUR', '52721256': 'BronziousMaximus',
             '81753210': 'Doctor Ag0ne', '34049984': 'AlphaBraver', '74552257': 'Mrshwin', '35020263': 'Axgold',
             '45314870': 'MomoChocobo', '65192131': 'jessiemay1993', '67949358': 'MLCorner', '47048001': 'nandochip',
             '32557811': 'Talk No Jutsu', '35688873': 'EnjuXD', '390241': 'the warrriorr', '25269212': 'xleb',
             '19046502': 'NID OR OPEN MID'}
df = pd.read_csv('final_roster2.csv', header=None, names=['userID', 'itemID', 'rating'])
mean = df['rating'].mean()
dfreader = Reader(rating_scale=(1, 100))
data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], dfreader)
# trainset, testset = train_test_split(data, shuffle=False, test_size=1)
trainset = data.build_full_trainset()

algo = SVD()
print("Generating algorithm... (This may take a while)")
algo.fit(trainset)
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
print("All ready!")
while True:
    summ_name = input("What is your summoner name?\n")  # "Naru"
    summ_id, ratings_dict = get_mastery(summ_name)
    if ratings_dict == "ERROR":
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
            ratings_dict['rating'].append(mean)
    dataframe = df.append(pd.DataFrame(ratings_dict))
    data = Dataset.load_from_df(dataframe[['userID', 'itemID', 'rating']], dfreader)
    temp, testset = train_test_split(data, shuffle=False, test_size=length)

    # Rating table should be {User, Champion, CMP}
    # Define the format
    # reader = Reader(line_format='user item rating', sep=',',rating_scale=(1, 100), skip_lines=1)
    # data = Dataset.load_from_file('final_roster2.csv', reader=reader)
    # trainset = data.build_full_trainset()

    # testset = trainset.build_anti_testset()

    # Get the results from applying the algorithm to the summoner
    predictions = algo.test(testset, verbose=False)
    top_n = get_top_n(predictions, 'max')

    # Print the recommended items for each user
    for uid, user_ratings in top_n.items():
        # print(summoners[str(uid)], [(champ_map[str(iid)], riid) for (iid, riid) in user_ratings])
        output = "For " + summoners[str(uid)] + ", I recommend: "
        for (iid, _) in user_ratings:
            output += champ_map[str(iid)] + ", "
        output = output[:-2] + "!\n"
        print(output)
        # print(summoners[str(uid)], [(champ_map[str(iid)]) for (iid, _) in user_ratings])
        # print([riid for (_, riid) in user_ratings])
        # print(uid, [(iid, riid) for (iid, riid) in user_ratings])
print("DONE!")
