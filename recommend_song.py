#coding: UTF-8
from requests_oauthlib import OAuth1Session
import json
import twitkey
import requests
import sys, urllib
import os.path
import time
import matplotlib as plt
from matplotlib import rcParams
# rcParams['font.family']= "MS Gothic"
import numpy as np
import glob
import MeCab
import pandas as pd
from janome.tokenizer import Tokenizer
from gensim.models import word2vec
import re

from sklearn import preprocessing

# uid: screen_name
def recommend_song(uid, status_id):
    twitter = OAuth1Session(twitkey.twkey["CONSUMER_KEY"], twitkey.twkey["CONSUMER_SECRET"], twitkey.twkey["ACCESS_TOKEN"], twitkey.twkey["ACCESS_TOKEN_SECRET"])

    response=twitter.get(
        f'https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={uid}')
    res = response.text

    res = json.dumps(res, indent=2)

    def wakati(sentence):
        t = Tokenizer()
        words = []
        for token in t.tokenize(sentence, stream=True):
            words.append(token.base_form)
        return words

    def getVector(words):
        tweet_vec = [0] * 50
        error = 0
        for word in words:
            try:
                tweet_vec += model.wv[word]
            except:
                error += 1
        try:
            tweet_vec = tweet_vec/len(words)
        except:
            error += 1
        return tweet_vec

    model = word2vec.Word2Vec.load("./word2vec_models/word2vec.gensim.model")
    def getTwitterDF(uid):
        twitter = OAuth1Session(twitkey.twkey["CONSUMER_KEY"], twitkey.twkey["CONSUMER_SECRET"],
                                twitkey.twkey["ACCESS_TOKEN"], twitkey.twkey["ACCESS_TOKEN_SECRET"])

        def delete_url(text):
            ret = re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)", "" ,text)
            return ret

        def delete_user_id(text):
            ret = re.sub(r"(@.+)", "" ,text)
            return ret

        def delete_line(text):
            return text.replace("\n"," ") 

        def get_tweets_list():
            max_id = None
            tweets = []
            for i in range(0, 8):
                url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
                if max_id:
                    params = {'screen_name': uid, "count": 200, "include_rts": False}
                else:
                    params = {'screen_name': uid, "count": 200,
                            "include_rts": False, "max_id": max_id}

                res = twitter.get(url, params=params)
                if res.status_code == 200:
                    r = json.loads(res.text)
                    obj = [tweet for tweet in r]
                    max_id = obj[-1]["id"]
                    tweets += [[tweet["text"], tweet["id"]] for tweet in r]

            return tweets

        def isalpha(s):
            alphaReg = re.compile(r'^[a-zA-Z]+$')
            return alphaReg.match(s) is not None

        stop_words = []

        stop_words.append("ない")
        stop_words.append("いい")
        stop_words.append("する")
        stop_words.append("いる")
        stop_words.append("てる")
        stop_words.append("なる")
        stop_words.append("れる")
        stop_words.append("ある")


        def split_text(text, filter=["動詞", "形容詞", "形容動詞", "名詞"]):
            tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
            text = unicodedata.normalize('NFC', text)
            tagger.parse("")
            # 形態素解析の結果をリストで取得、単語ごとにリストの要素に入ってる
            node = tagger.parseToNode(text)
            result = []
            #助詞や助動詞は拾わない
            while node is not None:
                #日本語の処理
                if node.surface.isalnum():
                    if isalpha(node.surface):
                        pass

                    else:
                        # 品詞情報取得
                        # Node.featureのフォーマット：品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
                        hinshi = node.feature.split(",")[0]
                        if hinshi in filter:
                            word = node.feature.split(",")[6]
                            if word not in stop_words and not isalpha(word):
                                result.append(word.replace("*", ""))

                node = node.next

            return " ".join(result)

        data = get_tweets_list()

        df = pd.DataFrame(data, columns=["tweet", "id"])
        # df["tweet"]=pd.Series(get_tweets_list())

        # ハッシュタグの#消去
        df["tweet"] = df["tweet"].str.replace("#", "")
        # @ユーザー名消去
        df["tweet"] = df["tweet"].map(lambda x: delete_user_id(str(x)))
        # URL消去
        df["tweet"] = df["tweet"].map(lambda x: delete_url(str(x)))
        # URL消去
        df["tweet"] = df["tweet"].map(lambda x: delete_line(str(x)))
        df = df[df["tweet"] != ""]

    #     df["words"] = df["tweet"].map(lambda x: split_text(x))

    #     print(df)
        return df
    df = getTwitterDF(uid)
    df = df.drop_duplicates(subset="id")

    df["words"] = ""
    for index, row in df.iterrows():
        wakati_result = wakati(row[df.columns.get_loc("tweet")])
        df.at[index, "words"] = wakati_result

    def cos_sim(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    df["vec"] = ""
    for index, row in df.iterrows():
        df.at[index, "vec"] = getVector(row[df.columns.get_loc("words")])

    df_song = pd.read_csv("./lyrics.csv")
    df_song = df_song.rename(columns = {"song":"song_name","lyrics":"lyric", "word":"words"})

    df_song["words"] = ""
    for index, row in df_song.iterrows():
        wakati_result = wakati(row[df_song.columns.get_loc("lyric")])
        df_song.at[index, "words"] = wakati_result
        
    df_song["vec"] = ""
    for index, row in df_song.iterrows():
        df_song.at[index, "vec"] = getVector(row[df_song.columns.get_loc("words")])

    df["song"] = ""
    df["score"] = ""

    for index, row in df.iterrows():
        vec_tweet = row[df.columns.get_loc("vec")]

        vec_song = df_song.vec.tolist()

        score_list = []
        for vec in vec_song:
            score_list.append(cos_sim(vec,vec_tweet))
        df.at[index, "song"] = df_song.at[score_list.index(max(score_list)), "song_name"]
    #     df.at[index, "score"] = max(score_list)
        try:
            df.at[index, "score"] = str(max(score_list))
        except:
            error = 1
    df.score = df.score.astype("float")

    df_result = df.song.value_counts().reset_index()

    result = df_result.at[0, "index"]

    df = df.drop_duplicates(subset="id")
    df = df.sort_values("score", ascending=False)

    df[df.song == result].reset_index(drop=True).at[0, "tweet"]


    # x, y ... pandas.series
    import matplotlib.pyplot as plt

    def rader_plot(x, y):
        pi = 3.1415
        
        # number of variable
        plt.figure(figsize=(8,8))

        categories=x.values.tolist()
        N = len(categories)

        # We are going to plot the first line of the data frame.
        # But we need to repeat the first value to close the circular graph:
        values = [s for s in y.values.tolist()]

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]


        # Initialise the spider plot
        ax = plt.subplot(111, polar=True)

        # Draw one axe per variable + add labels labels yet
        plt.xticks(angles, categories, color='grey', size=25)

        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([0.25, 0.5, 0.75, 1], ["25%","50%","75%","100%"], color="grey", size=7)
        plt.ylim(0,1)
        
        angles.append(angles[0])
        values.append(values[0])

        # Plot data
        ax.plot(angles, values, linewidth=1, linestyle='solid')

        # Fill area
        ax.fill(angles, values, 'b', alpha=0.1)
        filename = f"{uid}_{status_id}.png"
        plt.savefig(filename)
        return filename

    ##groupby mean

    df_score = df.groupby('song').mean().reset_index()
    df_score["score_std"] = preprocessing.minmax_scale(df_score.score)
    filename = rader_plot(df_score["song"], df_score["score_std"])

    return result, filename
