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


class ShortTweetID(BModel):
        id = IntegerField(primary_key=True,unique=True)
        original_tweet_id = ForeignKeyField(Tweet, to_field='tweet_id')
        short_tweet_id = IntegerField()

        class Meta:
             db_table = 'short_tweet'


class VerifiedAnswers(BModel):
       verified_id = IntegerField(primary_key=True,unique=True)
       verfied_short_id = ForeignKeyField(ShortTweetID, to_field='short_tweet_id')
       answer = TextField()
       user_who_verified = ForeignKeyField(User, to_field='user_id',unique=False)


       class Meta:
             db_table = 'verified_answers'

#Save the info of the tweets that have the correct format #wikianswer
class AnswerTweets(BModel):
        answer_tweet_id = IntegerField(primary_key=True,unique=True)
        user = ForeignKeyField(User, to_field='user_id', related_name='user',unique=False)
        tweet_message_answer =  ForeignKeyField(Tweet, to_field='tweet_id')
        woman = TextField()
        reason = TextField()
        has_been_verified = BooleanField(default=False)
        class Meta:
             db_table = 'answers_user'

class User_Asked_toVerify(BModel):
        user_asked_id = IntegerField(primary_key=True,unique=True)
        user_who_verified = ForeignKeyField(User, to_field='user_id',unique=False)
        verfied_short_id = ForeignKeyField(ShortTweetID, to_field='short_tweet_id')
        original_tweet_id = ForeignKeyField(Tweet, to_field='tweet_id')
        date_sent = DateTimeField()
        class Meta:
             db_table = 'users_targeted'

class PointsGiven(BModel):
        answer_tweet_id = IntegerField(primary_key=True,unique=True)
        #Saves the information regarding the points given to the user
        user_who_gave_point = ForeignKeyField(User, to_field='user_id', related_name='user_who_gave_poin',unique=False)
        user_who_received_point = ForeignKeyField(User, to_field='user_id', related_name='user_who_received_point',unique=False)
        tweet_with_answer = ForeignKeyField(Tweet, to_field='tweet_id', related_name='user_who_received_point',unique=False)
        #+1 or -1
        point = DecimalField(primary_key=False,unique=False)

        class Meta:
             db_table = 'points_given'



if __name__ == '__main__':
     try:
        db.connect()
        db.create_tables([User,Tweet,AnswerTweets,PointsGiven,User_Asked_toVerify,ShortTweetID,VerifiedAnswers])
     except OperationalError as e:
          print('Error: ', e)