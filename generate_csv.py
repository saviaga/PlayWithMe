from get_leaderboard import *
import csv

def prepareLoginData(ck,cs,at,atc):
    '''
    Autentica al Bot con las credenciales que obtiene de inforetentionbot.py
    :param botname: nombre del bot
    :return: api autenticada
    '''

    CONSUMER_KEY =ck
    CONSUMER_SECRET =cs
    ACCESS_KEY =at #keep the quotes, replace this with your access token
    ACCESS_SECRET =atc #keep the quotes, replace this with your access token secret
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def get_data():

    db=SqliteDatabase('retention.db')
    db.connect()
    answers = AnswerTweets.select()
    with open('test.csv', 'w') as fp:
        c = csv.writer(fp)
        for a in answers:
            user=api.get_user(a.user.user_id)
            username= user.screen_name
            print(username,a.woman," ", a.reason)
            data1 = "@"+username
            data2= a.woman
            data3= a.reason
            c.writerow((data1, data2, data3))


user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]
api=prepareLoginData(ck,cs,at,atc)

get_data()