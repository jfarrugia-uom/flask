import ast
import numpy as np
import pandas as pd
import pickle
from scipy import spatial

from gensim.models import word2vec
from py2neo import Graph, Node, Relationship
import os

# initialise model
cur_dir = os.path.dirname(__file__)
print "Initialising model...(1)"
model = word2vec.Word2Vec.load(os.path.join(cur_dir,"200features_30minwords_10context"))
print "Initialising review_vector...(2)"
review_vectors = pickle.load(open(os.path.join(cur_dir,'review_vector.pkl'), 'rb'))
print "Initialising original Toronto reviews...(3)"
pd_review = pickle.load(open(os.path.join(cur_dir, 'pd_review.pkl'), 'rb'))

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
graph = Graph(url + '/db/data/')


class Restaurant:
	def __init__(self, identifier):
		self.identifier = identifier
	
	def find(self):
		resto = graph.find_one('Business', 'id', self.identifier)
		return resto
		
	def get_sentiments(self, sentiment_type):
		query='''
		MATCH (n:Business)-[s]->(f) 
		where n.id={id} 
		and type(s) = {sentiment_type}
		with n,f,s order by s.adjective
		with type(s) as sentiment_type, n, f.name as feature_name, 
		collect({adj:s.adjective, text:s.sents,weight:s.weight}) as adjs, 
		max(s.weight) as max_weight return 
		sentiment_type, n.id as id, n.name as name, 
		n.stars as stars, n.reviews as reviews, n.category as category, 
		feature_name, adjs, max_weight order by max_weight desc, feature_name
		'''
		return graph.run(query, id=self.identifier, sentiment_type=sentiment_type)
		

# return restaurants with same features as in feature_list
def find_similar_sentiment_restaurants(feature_list):
		
	header = 'match(b:Business)-'
	body = ""
	for i, f in enumerate(feature_list):
		f = ast.literal_eval(f)
		body += '{node}[:{sentiment_type}] -> (:Feature{{name:"{feature_name}"}}),'.format(
			node = "(b)-" if i > 0 else "",
			sentiment_type = f[0], 
			feature_name = f[1])
	tail = ' return distinct b.name, b.id limit 25'
	query = header + body[:-1] + tail
	return graph.run(query)


# create vector average of search string to be able to find similar restaurants 
# based on review word similarity
def __convert_review_feature_vector(word_list, model, feature_count):
	# initialise array of length feature_count (200 )
	feature_vector = np.zeros((feature_count,), dtype='float32')
	# stores count of words that are features in learned vocab
	word_count = 0.
	# convert learned vocab to set for faster processing
	vocab_set = set(model.wv.index2word)
	# iterate over words in word_list, adding feature vectors together
	for word in word_list:
		if word in vocab_set:
			word_count += 1
			feature_vector = np.add(feature_vector, model.wv[word])
	
	# finally divide feature_vector by number of words ot get arithmetic vector mean
	feature_vector = np.divide(feature_vector, word_count)
	return feature_vector

# given a search string compute the cosine similarity of the search string transformed in
# 200 dimension word vector space and the review documents (similarly transformed)
def search_for_restaurants(search_string):
	
	search_vect = __convert_review_feature_vector(search_string.split(), model, 200)
	distances = []
	for rv in review_vectors:
		distances.append(np.round(spatial.distance.cosine(search_vect, rv),3))
    	
	_result = [(pd_review["name"][x], pd_review["id"][x], distances[x],\
				True if Restaurant(pd_review["id"][x]).find() else False)
				for x in np.argsort(distances)[:20]]

	return _result	
	

