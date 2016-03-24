import tweepy
from create_retention_database import User,Tweet, PointsGiven, AnswerTweets
import datetime
from bot import *


def check_retetion(the_bot,user):
    print("user: ",user[1:])
    user_name = user[1:]
    user_id = the_bot. get_user_id_from_screen_name(user_name)
    print("user_id: ",user_id)
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
            if (datetime.datetime.now() - itemx.created_date) > datetime.timedelta(1):

                print("more than 24 hours have passed: ", itemx.user_tweets.user_id)
                #add a row to the pointsgivent table with a -0.25 point
                PointsGiven.create(user_who_gave_point = user_id,user_who_received_point =itemx.user_tweets.user_id,tweet_with_answer = 000,point = -0.25 )
                #let know the user each day the number of points that he has lost, maybe a private message(dont' know if the user has to follow the bot)???
                message = "@"+itemx.user_tweets.screen_name+ " you lost a quarter of a point, you didn't participate in the last 24 hours"
                the_bot.update_status( message )

                break
            dates [itemx.user_tweets.user_id] = itemx.created_date

if __name__ == '__main__':


    print("antes de procesar archivo")
    user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]

    the_bot = Bot(user,ck,cs,at,atc)
    check_retetion(the_bot,user)