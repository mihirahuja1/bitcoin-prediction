import numpy as np
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from collections import Counter
import tweepy
import _pickle
import h5py
import sqlite3
import datetime



def most_common(lst):
    return max(set(lst), key=lst.count)


def load_offline(str):
    with open(str, 'rb') as f:
        dump = _pickle.load(f)
    return dump


word2index = load_offline('app/static/models/word_dict.pkl')

def init_model():
	lstm_model = load_model('app/static/models/lstm_1.h5') 
	cnn_model = load_model('app/static/models/cnn.h5')
	perceptron_model = load_model('app/static/models/percept_1.h5') 
	cnn_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
	bilstm_model = load_model('app/static/models/bilstm.h5')
	lstm_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
	perceptron_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
	graph = tf.get_default_graph()
	return lstm_model, perceptron_model, bilstm_model, cnn_model, graph


lmodel, percep, bilstm, cnn, graph = init_model()

auth = tweepy.OAuthHandler('8cBEjwKgM262KDcoJExVPgfwU','Bp0Ij0IcUqUXLcIJOItHXSCOgwSIUp9gK4upWBVjdiORB5ucAH')
auth.set_access_token('390663782-oBFE7dUk61hQ1cE5ljHIrtBgawdWXJitvxxxD2Ye','B21Ac6m4QF4piwpK4KMu9SMoiN6BshBh2Fc2Fj2jmps6o')


api = tweepy.API(auth)


def pencode(text):
	vector = np.zeros(len(word2index))
	for i, word in enumerate(text.split(' ')):
		try:
			vector[word2index[word]] = 1
		except KeyError:
			vector[i] = 0
	return vector


def lencode(text):
    vector = []
    for word in text.split(' '):
        try:
            vector.append(word2index[word])
        except KeyError:
            vector.append(0)
    padded_seq = pad_sequences([vector], maxlen=100, value=0.)
    return padded_seq


def lencode_cnn(text):
    vector = []
    for word in text.split(' '):
        try:
            vector.append(word2index[word])
        except KeyError:
            vector.append(0)
    padded_seq = pad_sequences([vector], maxlen=200, value=0.)
    return padded_seq


def get_most_count(x):
    return Counter(x).most_common()[0][0]

def get_date():
	d = datetime.date
	return str(d.today())
	

def predictor(query, c_sqlite, conn, currency, current_price):
	with graph.as_default():
		lout = lmodel.predict(lencode(query))
		cnn_out = cnn.predict(lencode_cnn(query))
		percept_out = percep.predict(np.expand_dims(pencode(query), axis=0))
		lout = np.argmax(lout, axis=1)
		cnn_out = np.argmax(cnn_out, axis=1)
		percept_out=np.argmax(percept_out, axis=1)
		bilstm_out = bilstm.predict(lencode(query))
		bilstm_out = np.argmax(bilstm_out, axis=1)
		var = [lout.tolist()[0], percept_out.tolist()[0], bilstm_out.tolist()[0], cnn_out.tolist()[0]]
	
	c = c_sqlite
	c.execute("INSERT INTO sentiments VALUES (?,?,?,?)", (get_date(), get_most_count(var),current_price, currency))
	conn.commit()

	return var


def get_db_results(c_sqlite, currency):
	c = c_sqlite
	db_date_list = []
	db_percent_list = []
	currency = currency
	for row in c.execute('SELECT timedate, SUM(case when sent=0 then 1 else 0 end) AS `negative`, SUM(case when sent=1 then 1 else 0 end) AS `positive`, COUNT(sent) AS `total` FROM sentiments where currency=? GROUP BY timedate', [currency]):
		db_date_list.append(row[0])
		db_percent_list.append((row[2]/row[3])*100)
	
	return db_date_list, db_percent_list


def processing_results(query, currency, current_price):
	conn = sqlite3.connect("app/static/tweet.db",check_same_thread=False)

	c = conn.cursor()

	predict_list = []
	line_sentiment = []
	for t in query:
		if not t == '':
			p = predictor(t, c, conn, currency, current_price)
			line_sentiment.append(most_common(p))
			predict_list.append(p)

	data = {'LSTM network': 0,
			'Perceptron network':0,
			'Bi-LSTM':0,
			'Convolutional Neural Network':0
		}

    # overal per sentence
	predict_list = np.array(predict_list)
	i = 0
	for key in data:
		data[key] = get_most_count(predict_list[:, i])
		i += 1

	# all the sentences with 3 emotions
	predict_list = predict_list.tolist()
	emotion_sents = [0, 0]
	for p in predict_list:
		if most_common(p) == 0:
			emotion_sents[0] += 1
		else:
			emotion_sents[1] += 1

	# overall score
	score = most_common(list(data.values()))
	
	db_date_list, db_percent_list = get_db_results(c, currency)
	conn.close()
	return data, emotion_sents, score, line_sentiment, query, len(query), (db_date_list, db_percent_list)
