# Import
from sklearn.feature_extraction.text import CountVectorizer
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import os

# Define as chaves
consumer_key =  os.environ['tweety_consumer_key']
consumer_secret = os.environ['tweety_consumer_secret']
access_token = os.environ['tweety_access_token']
acess_token_secret = os.environ['tweety_acess_token_secret']

# Faz a autenticacao
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, acess_token_secret)

# Cria o banco de dados
conn = MongoClient('localhost', 27017)
database = conn.get_database('twitterdatabase')
col = database.get_collection('tweets')

key_words = ['nintendo', 'zelda', 'super mario']

class MyListener(StreamListener):

    def __init__(self, col):
        super().__init__()
        self.__col__ = col
    
    def on_status(self, status):
        obj = { 'created_at': status.created_at, 'id_str': status.id_str, 'text': status.text }
        tweetind = self.__col__.insert_one(obj).inserted_id
        print(obj)
        return True

myListner = MyListener(col)
mystream = Stream(auth, listener = myListner)

mystream.filter(is_async=True, track=key_words, languages=['pt'])
mystream.disconnect()

dataset = [{ "created_at:": item["created_at"], "text": item["text"]  } for item in col.find()]
df = pd.DataFrame(dataset)

cv = CountVectorizer()
count_matrix = cv.fit_transform(df.text)

word_count = pd.DataFrame(cv.get_feature_names(), columns=["word"])
word_count["count"] = count_matrix.sum(axis=0).tolist()[0]
word_count = word_count.sort_values("count", ascending=False).reset_index(drop=True)
word_count[:50]



