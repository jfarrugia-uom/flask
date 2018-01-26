# import word2vec dependency
import ast
from .models import search_for_restaurants, Restaurant, find_similar_sentiment_restaurants
from flask import Flask, request, session, redirect, url_for, render_template, flash 
import pandas as pd

# get Flask application instance
app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/search_restaurant', methods=['POST'])
def search_restaurant():
	if request.method == 'POST':
		search_string = request.form['resto_search_string']
		results = search_for_restaurants(search_string)
		#flash(search_string)
		return render_template('first_results.html', 
		search_string=search_string, results=results)

@app.route('/sentiment/<restaurant>')
def sentiment(restaurant):
	resto = Restaurant(restaurant).find() 
	if not resto:
		# display error if restaurant is not found in neo4j database
		flash('Restaurant %s not found in sentiment database.' % (restaurant))
		return redirect(url_for('index'))
	else:		
		sentiment_list = []
		# concatenate positive and negative sentiments together
		sentiment_list.append(Restaurant(restaurant).get_sentiments('POSITIVE_SENTIMENT').data())
		sentiment_list.append(Restaurant(restaurant).get_sentiments('NEGATIVE_SENTIMENT').data())

		# display the sentiments for debugging reasons
		for sentiment_type in sentiment_list:
			for sentiment in sentiment_type:
				print sentiment['feature_name'], len(sentiment['adjs']), sentiment['sentiment_type']
	
		return render_template(
			'sentiment.html',
			resto=resto,
			sentiments=sentiment_list
		)

@app.route('/similar_sentiment', methods=['POST'])
def similar_sentiment():
	if request.method=='POST':
		#compose search query
		sentiment_criteria = request.form.getlist("search_by")
		#print sentiment_criteria
		similar_restaurants = find_similar_sentiment_restaurants(sentiment_criteria)
		#print similar_restaurants.data()
		return render_template(
			'similar_sentiment.html',			
			sentiment_criteria=[ast.literal_eval(x) for x in sentiment_criteria],
			results = similar_restaurants
		)
