import tweepy

class Bot:
    def __init__(self,name, consumer_key, consumer_secret, access_token,access_token_secret):
        self.botname = name
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        self.user = self.api.get_user(self.botname)
        self.user_id =self.api.get_user(self.botname).id_str




    def create_favorite(self,idTweet):
        self.api.create_favorite(idTweet)

    def update_status(self,message):
        self.api.update_status(status=message)

    def get_user_id(self,user_id):
        user_id=int(self.api.get_user(user_id).id_str)
        return user_id

    def get_user_id_from_screen_name(self,name):
        user_id=self.api.get_user(screen_name=name)
        return user_id.id_str



    def get_screen_name(self,user_id):
        screen_name = self.api.get_user(user_id).screen_name
        return screen_name

