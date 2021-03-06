import tweepy
from peewee import *
from create_retention_database import User,Tweet, PointsGiven, AnswerTweets
from play_with_retention import *

import datetime
def check_retetion():
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
        #print("now",datetime.datetime.now())
        for itemx in points:
            # more than 24 hours passed
            if (datetime.datetime.now() - itemx.created_date) > datetime.timedelta(1):

                print("more than 24 hours have passed: ", itemx.user_tweets.user_id)
                break
            dates [itemx.user_tweets.user_id] = itemx.created_date





            #CHECK IF THE LEADERBOARD CAN REST NON COMPLEATE NUMBERS (FLOAT NUMBERS)

def count_points_user(the_bot,user):
    print("user: ",user[1:])
    user_name = user[1:]
    user_id = the_bot.get_user_id_from_screen_name(user_name)
    print("user_id", user_id)
    points = PointsGiven.select(PointsGiven.point,PointsGiven.user_who_received_point).where(PointsGiven.user_who_received_point == user_id )
    sq = PointsGiven.select()
    tweetspositive = sq.where((PointsGiven.user_who_received_point ==  user_id ) & (PointsGiven.point == 1) )
    tweetsanswer = sq.where((PointsGiven.user_who_received_point ==  user_id ) & (PointsGiven.point == 2) )
    answer_points = (tweetsanswer.count())* 2
    tweetsnegative = sq.where((PointsGiven.user_who_received_point ==  user_id ) & (PointsGiven.point == -1) )
    quarterpoint = sq.where((PointsGiven.user_who_received_point ==  user_id ) & (PointsGiven.point == -0.25) )
    quarterpoint = (quarterpoint.count())*0.25
    totalpoints = (tweetspositive.count() + answer_points ) - (tweetsnegative.count()) - quarterpoint
    print("total points: ", totalpoints)
    return totalpoints


def get_leaderboard():
    users = []
    leaderboard = {}

    Point = PointsGiven.select(PointsGiven.user_who_received_point).distinct()
    for u in Point:
        users.append( u.user_who_received_point.user_id)
        print("user who received the point: ", u.user_who_received_point.user_id)

    for item in users:
        print("user:", item)
        points = PointsGiven.select(PointsGiven.point,PointsGiven.user_who_received_point).where(PointsGiven.user_who_received_point == item )

        sq = PointsGiven.select()
        tweetspositive = sq.where((PointsGiven.user_who_received_point == item) & (PointsGiven.point == 1) )
        print("count pos is: ",tweetspositive.count())
        print("user is:", item)

        tweetsanswer = sq.where((PointsGiven.user_who_received_point ==  item ) & (PointsGiven.point == 2) )
        answer_points = (tweetsanswer.count())* 2
        print("count answ is: ",answer_points)
        print("user is:", item)

        tweetsnegative = sq.where((PointsGiven.user_who_received_point == item) & (PointsGiven.point == -1) )
        print("count neg is: ",tweetsnegative.count())
        print("user is:", item)

        quarterpoint = sq.where((PointsGiven.user_who_received_point ==  item ) & (PointsGiven.point == -0.25) )
        quarterpoint = (quarterpoint.count())*0.25
        print("quarter is: ",)
        print("user is:", item)
        totalpoints = (tweetspositive.count() + answer_points ) - (tweetsnegative.count()) - quarterpoint
        leaderboard[item] = totalpoints
    sorted_dic = [(k,v) for v,k in sorted(
               [(v,k) for k,v in leaderboard.items()],reverse=True
               )
        ]

    return sorted_dic


def check_if_user_exists(user_id,the_bot):
    user_info = []
    query = User.select().where(User.user_id == user_id)
    if query.exists():
        # A user named "charlie" exists.
        print("Cool user exists..")
    else:
        print("user does not exists")
        username = the_bot.get_screen_name(user_id)
        user_info.append({'user_id':user_id,'screen_name':username})
        for item in user_info:
               user= User.create(user_id = item['user_id'],screen_name = item['screen_name'])



def process_leaderboard(the_bot,user_id):

    sorted_dic=get_leaderboard()

    send_leaderboard(the_bot,user_id,sorted_dic)

def send_leaderboard(the_bot,user_id,sorted_dic):
    user = the_bot.get_user_id(user_id)
    who_asked= the_bot.get_screen_name(user)
    who_asked = "@"+who_asked
    print("Printing Leaderboard for ", who_asked)
    message = ""
    count = 0
    for k,v in sorted_dic:
            if count < 4:
                count += 1
                username = the_bot.get_screen_name(k)
                tpoints = v
                player = "|" + str(username) + ": " + str(tpoints)+ "|"
                print (username,tpoints)
                message = message + player

            else:
                pass
    #print(message)
    message = who_asked + " Leaderboard: " +  message
    the_bot.update_status(str(message))

