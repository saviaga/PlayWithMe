
import shlex
from time import gmtime, strftime
from get_leaderboard import *


def authenticate(ck,cs,at,atc):
    consumer_key=ck
    consumer_secret=cs
    access_token=at
    access_token_secret=atc

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    l = StdOutListener()
    stream = tweepy.Stream(auth,l)
    return stream

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

    #3239553085
    idTweet=status.id_str
    #get the people mentioned in the tweet and adds the @ symbol
   # names=getPeopleMentionedTweet(message)
    #names["@"+screen_name]=0
    #print ("ScreenNameEE:"+screen_name)
    #print ("Message:"+message)

    #hashNames=getHashNames(names)
    #return date,status,screen_name,message,idTweet,names,hashNames
    return date,status,screen_name,message,idTweet, user_id

def clean_to_save( woman_reason):
    womamdb = woman_reason[0]
    womamdb = womamdb[2:-2]
    print("clean name:", womamdb)
    reasondb = woman_reason[1]
    reasondb = reasondb[2:-2]

    return womamdb,reasondb

def getPeopleMentionedTweet(message,user_id,idTweet):
    '''

    :param message: get the received tweet in which the bot was mentioned
    :return: the username of the people mentioned on the tweet including the bots username
    '''
    words=message.split()
    names={}

    db=SqliteDatabase('retention.db')
    db.connect()

    save_points = []
    save_answer = []
    points_answer = []

    user = api.get_user(user_id)
    username= user.screen_name
    username = "@"+username
    #answer = words.pop(0)
    if '*' in message:
        print("full: ",words)
        answer = words
        answer.pop(0)
        print("full2: ",answer)
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
            #Si hay mas de 2 tokens entonces solamente guarda los primeros dos
            print("woman_reason ",woman_reason)
            if cont > 2:
                ok=0
                pass
        womandb,reasondb = clean_to_save(woman_reason)
        print("woman: ",womandb)
        print("reason: ",reasondb)
        if ok == 1:
            api.update_status("Thanks for your suggestion " + username + " "+ womandb + " was added to our records")
        else:
            api.update_status(username + " We stored "  + womandb + ", " + reasondb)
        #print("who gaive the point for answer",api.me().screen_name)
        save_answer.append({'user': user_id,'tweet_message_answer':idTweet,'woman':womandb,'reason':reasondb})
        yo = api.me().screen_name
        userid = api.get_user(screen_name = yo)
        usergavepoint = userid.id
        for item in save_answer:
                print("item:", item)
                print("save answer lenght:",len(save_answer))
                AnswerTweets.create(user = item['user'],tweet_message_answer = item['tweet_message_answer'],woman = item['woman'],reason = item['reason'] )

                print("el user id es: ",usergavepoint)
                print("yo",yo)
        points_answer.append({'user_who_gave_point':usergavepoint,'user_who_received_point': user_id,'tweet_with_answer':idTweet,'point':2})
        #check if the user who receive the point has been stored

        for pa in  points_answer:
                print("item:", pa)
                print("save points lenght:",len(points_answer))
                PointsGiven.create(user_who_gave_point = pa['user_who_gave_point'],user_who_received_point =pa['user_who_received_point'],tweet_with_answer = pa['tweet_with_answer'],point = pa['point'] )
    for w in words:
        w=w.lower()


        if "@" in w:


            if not wordToFilter.lower() in w:

                if not botname in w:

                    print ("Name detected:"+w)
                    w=w.lower()
                    names[w]=0
        else:
            if "leaderboard" in w:
                print("you want to know the leaderboard")
                get_leaderboard(api,user_id)
    user = api.get_user(user_id)
    username= user.screen_name
    username = "@"+username

    x = 0
    for n in names:
        print ("Nombre:"+n+">>>>")
        user_who_received_point = api.get_user(n[:-2])
        user_who_received_point = user_who_received_point.id

        if n[-2:] == "++":
            print("awards a point to : ",n[:-2])

            total_points = count_points_user(api,n[:-2])
            total_points = str(total_points)

            api.update_status(status=str(n[:-2] +" 1 point given by "  + username  ))


            print("user id of who received the point: ",user_who_received_point)
            save_points.append({'user_who_gave_point':user_id,'user_who_received_point': user_who_received_point,'tweet_with_answer':idTweet,'point':1})
            check_if_user_exists(user_who_received_point,api)
        if n[-2:] == "--":
            print("minuses a point from: ",n)
            api.update_status(status=str(n[:-2] +" taken out 1 point by "  + username))
            save_points.append({'user_who_gave_point':user_id,'user_who_received_point': user_who_received_point,'tweet_with_answer':idTweet,'point':-1})
        print("save points: ",save_points)
        for item in save_points:
                    print("item:", item)
                    print("save points lenght:",len(save_points))
                    PointsGiven.create(user_who_gave_point = item['user_who_gave_point'],user_who_received_point =item['user_who_received_point'],tweet_with_answer = item['tweet_with_answer'],point = item['point'] )

                    print("saved to db")

    db.close()
       #REPLIES WITH ++ OR --
#the reply is the name of the bot,the name of th user and ++ or --


    #ANALIZE IF THE ANSWER HAS A ++ THEN UPDATE THE TABLE WITH THE USER POINT#
    # Updates the user info table with the point given

     #   '''
     # Table: Points Given
     # ID USER | ID_TWEET | POINT GIVEN | DATE OF POINT GIVEN

     #   '''

    return names


#override tweepy.StreamListener to add logic to on_status
class StdOutListener(tweepy.StreamListener):


    def on_status(self, status):
        db=SqliteDatabase('retention.db')

        try :
            db.connect()
            #list_user = []
            user_info = []
            tweet_info = []
            points_given = []
            print(status.user.id)
            print(status.user.screen_name)

            date,status,screen_name,message,idTweet,user_id=prepareDataIncomingMessage(status)
            api.create_favorite(idTweet)
            people=getPeopleMentionedTweet(message,user_id,idTweet)
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



if __name__ == '__main__':
    user,ck,cs,at,atc = [line.rstrip('\n') for line in open('my_twitter_info.txt','r')]

    print("antes de procesar archivo")


    stream=authenticate(ck,cs,at,atc)
    botname = user
    wordToFilter = botname
    api=prepareLoginData(ck,cs,at,atc)
    stream.filter(track=[wordToFilter])


