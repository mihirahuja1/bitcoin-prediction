from flask import Blueprint, request, render_template
from ..load import processing_results, api
import string
import tweepy
import re
import datetime
from exchanges.coindesk import CoinDesk


twitter_mod = Blueprint('twitter', __name__, template_folder='templates', static_folder='static')

ascii_chars = set(string.printable)
ascii_chars.remove(' ')
ascii_chars.add('...')


def takeout_non_ascii(s):
    return list(filter(lambda x: x not in ascii_chars, s))


@twitter_mod.route('/twitter', methods=['GET', 'POST'])
def twitter():
	if request.method == 'POST':
		bitcoin_price = CoinDesk().get_historical_data_as_dict(
			start=str(datetime.date.today()-datetime.timedelta(days=5)), 
			end=str(datetime.date.today()))
		tweets = []
		for tweet in tweepy.Cursor(api.search, 'bitcoin', lang='en').items(100):
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
		data, emotion_sents, score, line_sentiment, text, length, db_data = processing_results(tweets)

		bitcoin_price_list = []
		date_list = []
		for i in bitcoin_price:
			bitcoin_price_list.append(float(bitcoin_price[i]))
			date_list.append(i)
		
		return render_template('projects/twitter.html', data=[data, emotion_sents, score, zip(text, line_sentiment), length, date_list, bitcoin_price_list, db_data])
	else:
		return render_template('projects/twitter.html')

