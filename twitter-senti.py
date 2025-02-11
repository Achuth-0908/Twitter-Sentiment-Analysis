import tweepy
from textblob import TextBlob
import matplotlib.pyplot as plt


def authenticate_twitter_api():
    consumer_key = "5MlBDv9xGjForQy0eccj6ZkYq"
    consumer_secret = "yyrOhHqGLP5yBB7nXyMXr7NfwFRRHSa6scm3d8CEo9XqslDe3G"
    access_token = "1318581233853423617-7Oft19tN7532OUJIbRtaUndtYlC8bn"
    access_token_secret = "tT3WUpQZvVV3lu9oMsuIbatifFMSc3Z8iAC8X78smiVq2"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def get_tweets(api):
    search_term = input("Enter the keyword or hashtag to search tweets: ")
    tweet_count = int(input("Enter the number of tweets to fetch: "))
    language_filter = input("Enter the language filter (e.g., 'en' for English, or leave blank for all): ")

    tweets = api.search_tweets(q=search_term, count=tweet_count, lang=language_filter or None)

    tweet_texts = []
    sentiments = []

    print("\nAnalyzing Tweets...\n")

    for tweet in tweets:
        print(f"Tweet: {tweet.text}")
        analysis = TextBlob(tweet.text)
        sentiment = analysis.sentiment.polarity
        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
        print(f"Sentiment: {sentiment_label} (Polarity: {sentiment})\n")

        tweet_texts.append(tweet.text)
        sentiments.append(sentiment)

    return tweet_texts, sentiments

def visualize_sentiments(sentiments):
    positive = len([s for s in sentiments if s > 0])
    negative = len([s for s in sentiments if s < 0])
    neutral = len([s for s in sentiments if s == 0])

    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [positive, negative, neutral]
    colors = ['green', 'red', 'gray']
    explode = (0.1, 0.1, 0) 

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=explode)
    plt.axis('equal')
    plt.title('Sentiment Analysis of Tweets')
    plt.show()

if __name__ == "__main__":
    api = authenticate_twitter_api()
    tweet_texts, sentiments = get_tweets(api)

    if sentiments:
        visualize_sentiments(sentiments)
    else:
        print("No tweets found for the given search term.")
