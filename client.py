import os

import twitter as tw


class Client(object):
    last_id = None

    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        oauth = tw.OAuth(
            token,
            token_secret,
            consumer_key,
            consumer_secret
        )
        self.client = tw.Twitter(auth=oauth)

    def get_reply_user(self):
        if not self.last_id:
            tweets = self.client.statuses.mentions_timeline()
        else:
            tweets = self.client.statuses.mentions_timeline(since_id=self.last_id)
        if not tweets:
            return
        self.last_id = max(x["id"] for x in tweets)
        return {x['user']['screen_name'] for x in tweets}

    def reply(self, text, id_):
        tweet = self.client.statuses.update(status=text, in_reply_to_status_id=id_, auto_populate_reply_metadata=True)
        return tweet


API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

client = Client(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_SECRET_KEY)


def get_reply_user():
    return client.get_reply_user()

def reply(text, id_):
    return client.reply(text, id_)
