import pandas as pd
import scipy
from scipy import stats
import math


class Cluster:
    def __init__(self, tweet=None, id=None):
        if tweet is not None:
            self.data = pd.DataFrame(columns=('time', 'tweet_text', 'userID', 'country', 'lang'))
            self.data.loc[0] = [tweet.time, tweet.text, tweet.userID, tweet.country, tweet.lang]
            self.last_activity = tweet.time
            self.userDiversity = self.cal_userDiversity()
        else:
            self.data = pd.DataFrame(columns=('time', 'tweet_text', 'userID', 'country', 'lang'))
            self.last_activity = None
            self.userDiversity = 0
        if id is not None:
            self.id = id

    def addTweet(self, tweet):
        self.data.loc[len(self.data)] = [tweet.time, tweet.text, tweet.userID, tweet.country, tweet.lang]
        self.last_activity = tweet.time
        self.userDiversity = self.cal_userDiversity()

    def cal_userDiversity(self):
        user_counts = [x for x in self.data['userID'].value_counts()]
        n = sum(user_counts)
        # normalized entropy
        user_diversity = round(scipy.stats.entropy(user_counts) / math.log(n), 2)
        return user_diversity


class Tweet:
    def __init__(self, text, userID, time, country, lang):
        self.text = text
        self.userID = userID
        self.time = time
        self.country = country
        self.lang = lang

    def __str__(self):
        return 'Tweet Info : {} , {} , {} , {} , {}'.format(self.time, self.text, self.userID, self.country, self.lang)
