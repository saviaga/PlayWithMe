import tweepy
from peewee import *
from create_retention_database import User,Tweet, PointsGiven, AnswerTweets
import operator
import datetime


def count_points_user(api,user):
    print("user: ",user[1:])
    user_name = user[1:]
    user_id = api.get_user(screen_name = str(user_name) )
    print("user_id", user_id.id)
    points = PointsGiven.select(PointsGiven.point,PointsGiven.user_who_received_point).where(PointsGiven.user_who_received_point == user_id.id )
    sq = PointsGiven.select()
    tweetspositive = sq.where((PointsGiven.user_who_received_point ==  user_id.id ) & (PointsGiven.point == 1) )
    tweetsnegative = sq.where((PointsGiven.user_who_received_point ==  user_id.id ) & (PointsGiven.point == -1) )
    totalpoints = tweetspositive.count() - tweetsnegative.count()
    print("total points: ", totalpoints)
    return totalpoints


def get_leaderboard(api,user_id):
    users = []
    leaderboard = {}
    user = api.get_user(user_id)
    who_asked= user.screen_name
    who_asked = "@"+who_asked
    print("Printing Leaderboard for ", who_asked)
    Point = PointsGiven.select(PointsGiven.user_who_received_point).distinct()

    for u in Point:
        users.append( u.user_who_received_point.user_id)

    for item in users:
        #print("user:", item)
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
        totalpoints = (tweetspositive.count() + answer_points) - tweetsnegative.count()
        leaderboard[item] = totalpoints
    sorted_dic = [(k,v) for v,k in sorted(
               [(v,k) for k,v in leaderboard.items()],reverse=True
               )
        ]
    message = ""
    count = 0
    for k,v in sorted_dic:
            if count < 4:
                count += 1
                username = api.get_user(k).screen_name
                tpoints = v
                player = "|" + str(username) + ": " + str(tpoints)+ "|"
                print (username,tpoints)
                message = message + player

            else:
                pass
    #print(message)
    message = who_asked + " Leaderboard: " +  message
    api.update_status(status=str(message))
        # Display the sorted keys.

            #print("user: ",p.user_who_received_point.user_id)
            #print("point: ",p.point)

        #una vez listado el usuario y su punto se debe de sumarizar los puntos por usuario y mostrar la respuesta de mayor a menor




def check_if_user_exists(user_id,api):
    user_info = []
    query = User.select().where(User.user_id == user_id)
    if query.exists():
        # A user named "charlie" exists.
        print("Cool..")
    else:
        print("user does not exists")
        userid = api.get_user(user_id)
        username= userid.screen_name

        user_info.append({'user_id':user_id,'screen_name':username})
        for item in user_info:
               user= User.create(user_id = item['user_id'],screen_name = item['screen_name'])



