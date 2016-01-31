from peewee import *
import datetime

db=SqliteDatabase('retention.db')

class BModel(Model):
    class Meta:
        database = db

#Table to save the user basic information
class User(BModel):
        user_id = IntegerField(primary_key=True,unique=True)
        screen_name = CharField(max_length=255, unique=True,index=True)


        class Meta:
             db_table = 'users_info'

#Save the details of all the tweets exchanged betweet the bot and the users
class Tweet(BModel):
        tweet_id = IntegerField(primary_key=True,unique=True)
        user_tweets = ForeignKeyField(User, to_field='user_id', related_name='tweets')
        tweet_message = TextField()
        created_date = DateTimeField(default=datetime.datetime.now)

        class Meta:
             db_table = 'tweets'

#Save the info of the tweets that have the correct format #wikianswer
class AnswerTweets(BModel):
        answer_tweet_id = IntegerField(primary_key=True,unique=True)
        #Saves the tweets that contain the hashtag that was used to recruit the user
        user = ForeignKeyField(User, to_field='user_id', related_name='user',unique=False)
        tweet_message_answer =  ForeignKeyField(Tweet, to_field='tweet_id')
        woman = TextField()
        reason = TextField()
        class Meta:
             db_table = 'answers_user'

class PointsGiven(BModel):
        answer_tweet_id = IntegerField(primary_key=True,unique=True)
        #Saves the information regarding the points given to the user
        #user = ForeignKeyField(User, to_field='user_id', related_name='screenname')
        user_who_gave_point = ForeignKeyField(User, to_field='user_id', related_name='user_who_gave_poin',unique=False)
        user_who_received_point = ForeignKeyField(User, to_field='user_id', related_name='user_who_received_point',unique=False)
        #point_given_to = ForeignKeyField(User, to_field='user_id', related_name='point_given_to')
        tweet_with_answer = ForeignKeyField(Tweet, to_field='tweet_id', related_name='user_who_received_point',unique=False)
        #+1 or -1
        point = DecimalField(primary_key=False,unique=False)
        #format +1 or -1
        #points_givenbyuser = IntegerField(primary_key=False,unique=False)
        #always +1 as the user get 1 point from the bot for interacting with it
        #points_interactionbot = IntegerField(primary_key=False,unique=False)

        class Meta:
             db_table = 'points_given'



if __name__ == '__main__':
     try:
        db.connect()
        db.create_tables([User,Tweet,AnswerTweets,PointsGiven])
     except OperationalError as e:
          print('Error: ', e)