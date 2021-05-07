import snscrape
import os
import pandas as pd
import datetime as dt
import snscrape.modules.twitter as snstwitter
import time
import textblob
import matplotlib.pyplot as plt
import re
import emot
import emoji
from langdetect import detect, detect_langs

#function to get tweets using snscrape
def get_tweets(text_query,max_results):
    start_time = time.time()
    tweets_added = 0
    tweets_list = []
    start_date = dt.date(2021,4,27)
    until_date = dt.date.today()
    tweets = snstwitter.TwitterSearchScraper("{} since:{} until:{}".format(text_query,start_date,until_date)).get_items()
    for i,tweet in enumerate(tweets):
        if text_query in tweet.content:
            tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.username])

            tweets_added+=1
        if tweets_added == max_results:
            break
        end_time = time.time()
        if (end_time - start_time) > 1500:
            break
    return tweets_list

#function to clean tweets removing emojis, newlines, twitter handles etc 
def clean_tweets(text):
	emoji_pattern = emoji.get_emoji_regexp("en")
	text = re.sub(emoji_pattern,"",text)
	text = re.sub(r"@[a-zA-Z0-9_]+", '', text)
	text = re.sub(r"RT\s@\w+", '', text)
	text = re.sub(r"#[a-zA-Z0-9_]+", ' ', text)
	text = re.sub(r'\\n', '', text)
	text = re.sub(r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?", ' ', text)
	text = re.sub(r"&amp", ' ', text)

	return text

#function to filter out non english tweets using textblob
def translate_text(text):
    blob = textblob.TextBlob(text)
    lang = blob.detect_language()
    #return lang
    #lang = detect(text)
    if lang != "en":
        #text = blob.translate(to="en")
        #text = text.raw
        text = ""
    else:
        text = text
    return text

text_query = 'Doge Coin' #This is the search keyword
my_tweets = get_tweets(text_query, 200)
tweets_df = pd.DataFrame(my_tweets, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])

tweets_df['Text'] = tweets_df["Text"].apply(clean_tweets)

#iterates through the dataframe and creates a new column containing the language used in the tweet
for text in range(len(tweets_df)):
    blob = textblob.TextBlob(tweets_df.loc[text, 'Text'])
    lang = blob.detect_language()
    tweets_df['Language'] = lang

for lang in range(len(tweets_df)):
    if tweets_df.loc[lang, 'Language'] != 'en':
        print(tweets_df.loc[lang, 'Text'])

tweets_df['Polarity'] = tweets_df['Text'].map(lambda tweet: textblob.TextBlob(tweet).sentiment.polarity)
#This maps each tweet to the function textblob.TextBlob(tweet).sentiment.polarity to get it's polarity and then puts it into the column Polarity
tweets_df['Result'] = tweets_df['Polarity'].map(lambda pol: '+' if pol > 0.1 else '-')

#Specifies which tweets are positive(+) or negative(-)
positive = tweets_df[tweets_df.Result == '+'].count()['Text']
negative = tweets_df[tweets_df.Result == '-'].count()['Text']

#Visualizes the result as a bar plot
plt.bar([0, 1], [positive, negative], label=['Positive', 'Negative'], color=['green', 'red']) #[0, 1] for x axis and [positive, negative] for y axis
plt.legend()
plt.title(text_query)
plt.show()