import csv
import tweepy
from peewee import *
from create_retention_database import User,Tweet, PointsGiven, AnswerTweets,VerifiedAnswers,ShortTweetID

from bot import *
#from play_with_retention import *

#from get_leaderboard import *



def get_id_shortid():
    unique_ids=[]
    #from the verifiedanswers table make a select distinct to filters ids of users without repeating ids

    ids = VerifiedAnswers.select(VerifiedAnswers.verfied_short_id).distinct()

    for u in ids:
        try:
            unique_ids.append(u.verfied_short_id.short_tweet_id)
        #in case that the user gave a short id that does not correspond to a tweet id then just ignore it
        except:
            pass
    return unique_ids

def get_original_answer_and_mark(id):
    original_id = []
    db=SqliteDatabase('retention.db')
    db.connect()
    #get the original tweet id for each short_id
    answer = ShortTweetID.select(ShortTweetID.original_tweet_id).distinct().where(ShortTweetID.short_tweet_id == id)
    for a in answer:
        print("original tweetid: ",a.original_tweet_id.tweet_id)
        original_id.append(a.original_tweet_id.tweet_id)
         #marcar la pregunta como verificada, quiere decir que esa pregunta ya no se vuelve a mandar a los usuarios

    #get the original answer that belongs to that tweetid
        for oid in original_id:
            original_answer =AnswerTweets.select(AnswerTweets.user,AnswerTweets.woman,AnswerTweets.reason).where(AnswerTweets.tweet_message_answer ==oid)
            mark_as_verified =  AnswerTweets.update(has_been_verified=True).where(AnswerTweets.tweet_message_answer ==oid)
            mark_as_verified.execute()
            return original_answer

def count_correct_answer(id,the_bot):

    print("id: ",id)

    points = VerifiedAnswers.select(VerifiedAnswers.answer,VerifiedAnswers.verfied_short_id).where(VerifiedAnswers.verfied_short_id == id )
    tweetspositive = points.where((VerifiedAnswers.verfied_short_id ==  id ) & (VerifiedAnswers.answer == 'y') )
    #from verifiedanswer table check the number of Y answer for each id
    answer_points = (tweetspositive.count())
    #returns the points per answer
    return answer_points

def save_to_csv(original_answer,the_bot):
             with open('wikipedia.csv', 'a') as fp:
                    for oa in original_answer:
                        c = csv.writer(fp,delimiter=',')
                        user=the_bot.get_user_id(oa.user.user_id)
                        username= "@"+the_bot.get_screen_name(user)
                        print("userx ", username)
                        print("womanx ", oa.woman)
                        print("reasonx ", oa.reason)
                        c.writerow((username,oa.woman,oa.reason))

if __name__ == '__main__':
    #gets unique short ids from verifiedanswers table
    ids=get_id_shortid()

    user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]
    the_bot = Bot(user,ck,cs,at,atc)


    for id in ids:
        print("ids: ",id)
        answerpoints=count_correct_answer(id,the_bot)
        print("answerpoints",answerpoints)
        #if the answer has at least 4 Y then it can be added to the final CSV
        if (answerpoints>=2):
            #this returns the original answer that got 4 Y
             original_answer=get_original_answer_and_mark(id)


            #save it to a csv
             save_to_csv(original_answer,the_bot)



