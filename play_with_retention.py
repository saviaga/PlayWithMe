import shlex
from time import gmtime, strftime
from create_retention_database import *
from get_leaderboard import *
from bot import *



def authenticate(ck,cs,at,atc):
    consumer_key=ck
    consumer_secret=cs
    access_token=at
    access_token_secret=atc

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    l = StdOutListener()
    stream = tweepy.Stream(auth,l)
    return api,stream


def clean_to_save( woman_reason):
    womamdb = woman_reason[0]
    womamdb = womamdb[2:-2]
    print("clean name:", womamdb)
    reasondb = woman_reason[1]
    reasondb = reasondb[2:-2]

    return womamdb,reasondb



def prepareDataIncomingMessage(status):
    '''
    reads the tweet in which the bot was mentioned
    :param status:  is the tweet received
    :return: all the information retrieved from the message separated as variables
    '''

    year=strftime("%Y", gmtime())
    month=strftime("%m", gmtime())
    day=strftime("%d", gmtime())
    hour=strftime("%H", gmtime())
    minute=strftime("%M", gmtime())
    sec=strftime("%S", gmtime())

    date= datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(sec) )
    status.created_at = date
    screen_name=status.user.screen_name
    screen_name=screen_name.lower()
    message=status.text
    user_id = status.user.id
    idTweet=status.id_str
    return date,screen_name,message,idTweet, user_id

def process_tweet(message,user_id,idTweet):
    '''

    :param message: get the received tweet in which the bot was mentioned
           user_id: the id of the user who sent the tweet
           idTweet: the id of the tweet that received the bot
    :return: the username of the people mentioned on the tweet including the bots username
    '''
    names={}
    save_points = []
    save_answer = []
    points_answer = []
    ok=0

    #connect to the database
    db=SqliteDatabase('retention.db')
    db.connect()

    #split the tweet in words
    words=message.split()
    #the username of the user who sent the tweet
    username= the_bot.get_screen_name(user_id)
    username = "@"+username

    #check if the message is separated by * (meaning is a suggestion)

    #We can receive five types of tweets
    #Type 1: The message is just a random message where the bot is mentioned(Does nothing just stores it)
    #Type 2: The message has a suggestion in the form *Woman* *Reason*
    #Type 3: The message is a response to a verification tweet, so the user respons IDTweet -Y- or -N-
    #Type 4: The message is to give points or to take out points ++ --
    #type 5: The message is to get the leaderboard

    #checks if other users are being mentioned in the tweet
    for w in words:
        verified_answer = []
        w=w.lower()
        if "@" in w:
            if not wordToFilter.lower() in w:
                if not botname in w:
                    print ("Name detected:"+w)
                    w=w.lower()
                    names[w]=0
        #check if the word leaderboard is on the tweet
        #type 5: The message is to get the leaderboard
        elif "leaderboard" in w:
                print("you want to know the leaderboard")
                process_leaderboard(the_bot,user_id)


    #Type 2: The message has a suggestion in the form *Woman* *Reason*
    if '*' in message:
        print("full: ",words)
        answer = words
        #this instruction deletes the name of the bot at the begining of the message
        #converts: ['@letsviralizeit', '*bronco*', '*gobernador*']
        #to:  ['*bronco*', '*gobernador*']
        answer.pop(0)

        print("full2: ",answer)
        #this converts the list in a string
        #  *bronco* *gobernador*
        my_lst_str = ' '.join([str(mli) for mli in answer])
        print("full3 ",my_lst_str)

        lexer = shlex.shlex(my_lst_str)
        lexer.quotes = '*'

        print ('TOKENS:')
        cont= 0
        woman_reason=[]
        for token in lexer:
            print("token ",cont)
            cont += 1
            print (repr(token))
            if cont <= 2:
                woman_reason.append(repr(token))
                ok = 1
            #if more than two tokens are given then it just save the first two
            print("woman_reason ",woman_reason)
            if cont > 2:
                ok= 0
                pass
        womandb,reasondb = clean_to_save(woman_reason)
        print("woman: ",womandb)
        print("reason: ",reasondb)
        #if the tweet came correcty with 2 parameters "woman" "reason"
        if ok == 1:
            the_bot.update_status("Thanks for your suggestion " + username + " "+ womandb + " was added to our records")

        else:
        #if the tweet had more than 2 parameters
            the_bot.update_status(username + " We stored "  + womandb + ", " + reasondb)
        save_answer.append({'user': user_id,'tweet_message_answer':idTweet,'woman':womandb,'reason':reasondb})
        usergavepoint = int( the_bot.user_id)
        #stores the answer
        for item in save_answer:
                print("save answer lenght:",len(save_answer))
                AnswerTweets.create(user = item['user'],tweet_message_answer = item['tweet_message_answer'],woman = item['woman'],reason = item['reason'] )
                print("el user id es: ",usergavepoint)
        #stores the 2 points for correct answer
        points_answer.append({'user_who_gave_point':usergavepoint,'user_who_received_point': user_id,'tweet_with_answer':idTweet,'point':2})
        for pa in  points_answer:
                print("item:", pa)
                print("save points lenght:",len(points_answer))
                PointsGiven.create(user_who_gave_point = pa['user_who_gave_point'],user_who_received_point =pa['user_who_received_point'],tweet_with_answer = pa['tweet_with_answer'],point = pa['point'] )


    #Type 3: The message is a response to a verification tweet, so the user respons IDTweet -Y- or -N-
    if '.' in message:
        print("full: ",words)
        answer = words
        answer.pop(0)
        print("full2: ",answer)
        my_lst_str = ' '.join([str(mli) for mli in answer])
        print("full3 ",my_lst_str)

        lexer = shlex.shlex(my_lst_str)
        lexer.quotes = '.'

        print ('TOKENS:')
        cont1= 0
        short_answer=[]
        for token in lexer:
            print("token ",cont1)
            cont1 += 1
            print (repr(token))

            if cont1 <= 2:
                short_answer.append(repr(token))
                ok=1
            #Si hay mas de 2 tokens entonces solamente guarda los primeros dos
            print("woman_reason ",short_answer)
            if cont1 > 2:
                ok=0
                pass
        shortid,answer = clean_to_save(short_answer)
        print("woman: ",shortid)
        print("reason: ",answer)
        if ok == 1:
            vmessage = username + " thank you for your answer for: "+ shortid
            the_bot.update_status(vmessage)
        else:
            the_bot.update_status(username + " We stored "  + shortid + ", " + answer)


        short_answer.append({'user_who_verified': int(user_id),'verfied_short_id':int(shortid),'answer':answer})
        yo = api.me().screen_name
        userid = api.get_user(screen_name = yo)
        userverified = userid.id
        for v in short_answer:
                print("item:", v)
                print("elid: ",type(int(user_id)))

    #the bot must start listening for answers, then store each answert that has id and Y or N
    #[@bot 1023: Y]

        VerifiedAnswers.create(user_who_verified = v['user_who_verified'],verfied_short_id = v['verfied_short_id'],answer =  v['answer'])

        print("el user id es: ",userverified)
        print("yo",yo)

    #Type 4: The message is to give points or to take out points @user++  @user--LISTO
    #the for loop is in cas the user awards points to various users in the same tweet

    for n in names:
        user_who_received_point = the_bot.get_user_id(n[:-2])

        if n[-2:] == "++":
            print("awards a point to : ",n[:-2])

            the_bot.update_status(str(n[:-2] +" 1 point given by "  + username  ))
            print("user id of who received the point: ",user_who_received_point)
            save_points.append({'user_who_gave_point':user_id,'user_who_received_point': user_who_received_point,'tweet_with_answer':idTweet,'point':1})
            check_if_user_exists(user_who_received_point,the_bot)
            #verifies how may points the user has
            total_points = count_points_user(the_bot,n[:-2])
            total_points = str(total_points)
            print("total points: ",total_points)

        if n[-2:] == "--":
            print("minuses a point from: ",n)
            the_bot.update_status(str(n[:-2] +" taken out 1 point by "  + username))
            save_points.append({'user_who_gave_point':user_id,'user_who_received_point': user_who_received_point,'tweet_with_answer':idTweet,'point':-1})
        print("save points: ",save_points)
        for item in save_points:
                    #print("item:", item)
                    print("save points lenght:",len(save_points))
                    check_if_user_exists(user_who_received_point,the_bot)
                    PointsGiven.create(user_who_gave_point = item['user_who_gave_point'],user_who_received_point =item['user_who_received_point'],tweet_with_answer = item['tweet_with_answer'],point = item['point'] )
                    print("saved to db")

    db.close()
    return names



class StdOutListener(tweepy.StreamListener):


    def on_status(self, status):
        #opens database
        db=SqliteDatabase('retention.db')

        try :
            db.connect()
            user_info = []
            tweet_info = []
            #this is the user that sent the bot
            print("first print for try ",status.user.id)
            print("first print for try",status.user.screen_name)
            #gets the in reply status
            #if in reply status is different from null, then it means is a reply which means that i can catch
            #if it has a Y or N in the answer and if the answer is correct
            #although i need the id of the original tweet so i can match to which tweet is refering!!!!!damn!!
            print("in reply status id",status.in_reply_to_status_id)
            #this function extracts information from the incoming tweet
            date,screen_name,message,idTweet,user_id=prepareDataIncomingMessage(status)
            the_bot.create_favorite(idTweet)
            people=process_tweet(message,user_id,idTweet)
            print("The people_mentioned: ",people)
            user_info.append({'user_id':user_id,'screen_name':screen_name})
            tweet_info.append({'tweet_id':idTweet,'user_tweets':user_id,'tweet_message':message,'created_date':date})

            for itemr,itemh, in zip(user_info,tweet_info):

                try:
                    print("i am here", itemr['user_id'])
                    print("i am here", itemr['screen_name'])
                    print("i am here", itemh['tweet_id'])
                    print("i am here", itemh['user_tweets'])
                    print("i am here", itemh['tweet_message'])
                    print("i am here", itemh['created_date'])
                    #The following is the same as the short version Recruited.create(**itemr)
                    sq =  User.select().from_(User)
                    if sq.where(User.user_id == itemr['user_id']).exists():
                         tweet = Tweet.create(tweet_id = itemh['tweet_id'],user_tweets =itemh['user_tweets'],tweet_message = itemh['tweet_message'],created_date = itemh['created_date'] )
                         print(api.me().screen_name)
                         result2=tweet.save(force_insert=True)
                    else:
                         user= User.create(user_id = itemr['user_id'],screen_name = itemr['screen_name'])
                         tweet = Tweet.create(tweet_id = itemh['tweet_id'],user_tweets =itemh['user_tweets'],tweet_message = itemh['tweet_message'],created_date = itemh['created_date'] )

                         result= user.save(force_insert=True)
                         result2=tweet.save(force_insert=True)
                    db.close()

                except IntegrityError:
                    pass

        except Exception as e:
            print ("EXCEPTION :(", e)
            #pass

        def on_error(self, status):
            print ("EERROR"+str(status))














def identify_bot(user,ck,cs,at,atc):
    global the_bot
    the_bot = Bot(user,ck,cs,at,atc)
    wordToFilter = the_bot.botname

    return wordToFilter,user






if __name__ == '__main__':


    print("antes de procesar archivo")
    user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]
    wordToFilter,user=identify_bot(user,ck,cs,at,atc)
    global botname
    botname = user
    global api

    api,stream=authenticate(ck,cs,at,atc)
    stream.filter(track=[wordToFilter])





