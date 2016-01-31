import tweepy
from create_retention_database import User,Tweet, PointsGiven, AnswerTweets
import datetime

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

def check_retetion(api,user):
    print("user: ",user[1:])
    user_name = user[1:]
    user_id = api.get_user(screen_name = str(user_name) )
    print("user_id: ",user_id.id)
    users = []
    dates = {}
    #THIS FUCTION MUST RUN EVERY 24 HOURS AT THE SAME TIME EVERY DAY
    print("Checking user's retention")
    #from the tweets table make a select distinct to filters ids of users without repeating ids
    Point = Tweet.select(Tweet.user_tweets).distinct().order_by(Tweet.user_tweets)


    for u in Point:
        users.append( u.user_tweets.user_id)
        print("user:",u.user_tweets.user_id)
    #for each user check the last tweet from the user
    for item in users:

        points = (Tweet.select().where(Tweet.user_tweets == item).order_by(Tweet.user_tweets))
        for itemx in points:
            # more than 24 hours passed
            if (datetime.datetime.now() - itemx.created_date) < datetime.timedelta(1):

                print("more than 24 hours have passed: ", itemx.user_tweets.user_id)
                #add a row to the pointsgivent table with a -0.25 point
                PointsGiven.create(user_who_gave_point = user_id.id,user_who_received_point =itemx.user_tweets.user_id,tweet_with_answer = 000,point = -0.25 )
                #let know the user each day the number of points that he has lost, maybe a private message(dont' know if the user has to follow the bot)???
                message = "@"+itemx.user_tweets.screen_name+ " you lost a quarter of a point, you didn't participate in the last 24 hours"
                api.update_status(status = message )

                break
            dates [itemx.user_tweets.user_id] = itemx.created_date

user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]




api=prepareLoginData(ck,cs,at,atc)

check_retetion(api,user)