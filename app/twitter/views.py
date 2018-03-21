from flask import Blueprint, request, render_template
from ..load import processing_results, api
import string
import tweepy
import re
from exchanges.bitfinex import Bitfinex


BitPrice = Bitfinex().get_current_price()



twitter_mod = Blueprint('twitter', __name__, template_folder='templates', static_folder='static')

ascii_chars = set(string.printable)
ascii_chars.remove(' ')
ascii_chars.add('...')


def takeout_non_ascii(s):
    return list(filter(lambda x: x not in ascii_chars, s))


@twitter_mod.route('/twitter', methods=['GET', 'POST'])
def twitter():
	if request.method == 'POST':
		
		tweets = []
		for tweet in tweepy.Cursor(api.search, request.form['topic'], lang='en').items(100):
			text =re.sub(r'http\S+', '', tweet.text)
			emoji_pattern = re.compile("["
				u"\U0001F600-\U0001F64F"  # emoticons
				u"\U0001F300-\U0001F5FF"  # symbols & pictographs
				u"\U0001F680-\U0001F6FF"  # transport & map symbols
				u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
								   "]+", flags=re.UNICODE)
			text = (emoji_pattern.sub(r'', text)) # no emoji
			text = re.sub(r'@', '', text)
			text = re.sub(r'#', '', text)
			tweets.append(text)
		data, emotion_sents, score, line_sentiment, text, length = processing_results(tweets)

		return render_template('projects/twitter.html', data=[data, emotion_sents, score, zip(text, line_sentiment), length, [200,300,400,500,600]])
	else:
		return render_template('projects/twitter.html')

