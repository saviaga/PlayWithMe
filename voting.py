from peewee import *
from create_retention_database import AnswerTweets,ShortTweetID,User_Asked_toVerify
from play_with_retention import identify_bot
from bot import *

from get_leaderboard import *

# This script will control the Phase 2: Verify step in the game

#Bot asks experts to verify the information of the woman to be added to wikipedia

#The script should retrieve the answers from the db



def voting(the_bot,user):
    users = []
    tweet_to_verify = {}

    db=SqliteDatabase('retention.db')
    db.connect()
    print("Initiating Voting")
    #from the answertweets table make a select  to get tweets with answers
    ##################Pendientes###

    #cuando se corre el programa, debe de checar si esa pregunta ya fue hecha al usuario,
    #se debe guardar la fecha en que se le envio a que usuarios
    #si aun no se ha enviado entonces se recluta a los usuarios del leaderboard para las sigueintes preguntas y se crea el shortid
    #tambien se debe de tomar en cuenta que si el tweet aun no tiene los sufientes votos se deben de mandar a otras personas diferentes para que voten
    #saves the answers from answer_users that has not been verified
    answers = AnswerTweets.select().where(AnswerTweets.has_been_verified == False)

    #this for creates the short id table
    #the variable answer has all the information from the answer_user table
    ###############check that does not create duplicate rows , maybe unique = true?###
    for a in answers:
        #gets the original tweet id
        originalid= (a.tweet_message_answer.tweet_id)

        tweetid = str(originalid)
        #creates the short id
        answerid = tweetid[-5:]
        ShortTweetID.create(original_tweet_id = int(originalid),short_tweet_id = answerid)

        print("tweet:",answerid,a.woman, a.reason)
        tweets[tweetid] = answerid + ": " + a.woman + ", " + a.reason

    #this will create the users to target
    #get the 10 most participative users
    sorted_dict = get_leaderboard()
    count=0
    for k,v in sorted_dict:
            if count < 3:
                count += 1
                username = the_bot.get_screen_name(k)

                tpoints = v
                player = "|" + str(username) + ": " + str(tpoints)+ "|"
                users.append(username)
                print ("player: ",player)

    for u in users:
        print("the users to target: ",u)
        #and constructs a tweet  [@verifier 1023: Answer to verify- "Fridah Kahlo" "www.kahlo.com"]

        for  vv in tweets.values():
            message=('@'+u +' help us decide Y or N, ID'+ vv)
            tweet= User_Asked_toVerify.create(user_who_verified = id_user_who_verified,verfied_short_id = itemr['screen_name'])
            the_bot.update_status(message)
# |tweetid that was asked|Y or N | id of the user who answered| id of the tweet with the answer





if __name__ == '__main__':


    print("antes de procesar archivo")
    user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]

    the_bot = Bot(user,ck,cs,at,atc)
    voting(the_bot,user)

