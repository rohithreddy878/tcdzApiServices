from flask import jsonify, Flask, request, render_template, redirect, url_for, send_file
from flask_restful import Resource, reqparse
from sqlalchemy import or_, text
from ast import literal_eval
import re
import json
import os
from io import BytesIO

from model import db, Match, Delivery, Innings, Player, Team
import Constants

import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from wordcloud import WordCloud



# Ensure the necessary NLTK data is available
nltk.download('punkt')
nltk.download('stopwords')



class PlayerBatStrengthsResource(Resource):
    def __init__(self):
        self.tag = "PlayerBatStrengthsResource"

    def get(self, playerId,area):
    	cricbuzz_comms=[]
    	if(area=='fours'):
    		cricbuzz_comms=self.getPlayerFoursScoredData(playerId)
    	elif(area=='sixes'):
    		cricbuzz_comms=self.getPlayerSixesScoredData(playerId)
    	elif(area=='outs'):
    		cricbuzz_comms=self.getPlayerGotOutData(playerId)

    	return {'status': 'success', 'data': cricbuzz_comms}, 200

    def getPlayerFoursScoredData(self,playerId):
    	query = text(Constants.PLAYER_RUNS_SCORED_COMMS_QUERY)
    	queryRes = db.session.execute(query, {"playerIdParam": playerId,"runsParam":4})
    	queryResMaps = queryRes.mappings().all()
    	#print("queryResMaps: ",queryResMaps)
    	cricbuzz_comms=[]
    	i=1
    	for row in queryResMaps:
    		c=row["cricbuzz_commentary"]
    		length=self.extract_line_of_ball(c) if c else ""
    		line=self.extract_length_of_ball(c) if c else ""
    		comm ={'i':i,'text':c,  'line':line, 'length':length}
    		i=i+1
    		cricbuzz_comms.append(comm)
    	return cricbuzz_comms

    def getPlayerSixesScoredData(self,playerId):
    	query = text(Constants.PLAYER_RUNS_SCORED_COMMS_QUERY)
    	queryRes = db.session.execute(query, {"playerIdParam": playerId,'runsParam':6}).mappings().all()
    	cricbuzz_comms=[]
    	i=1
    	for row in queryRes:
    		c=row["cricbuzz_commentary"]
    		length=self.extract_line_of_ball(c) if c else ""
    		line=self.extract_length_of_ball(c) if c else ""
    		comm ={'i':i,'text':c,  'line':line, 'length':length}
    		cricbuzz_comms.append(comm)
    		i=i+1
    	return cricbuzz_comms

    def getPlayerGotOutData(self,playerId):
    	query = text(Constants.PLAYER_GOT_OUT_COMMS_QUERY)
    	queryRes = db.session.execute(query, {"playerIdParam": playerId}).mappings().all()
    	cricbuzz_comms=[]
    	i=1
    	for row in queryRes:
    		c=row["cricbuzz_commentary"]
    		length=self.extract_line_of_ball(c) if c else ""
    		line=self.extract_length_of_ball(c) if c else ""
    		comm ={'i':i,'text':c,  'line':line, 'length':length}
    		cricbuzz_comms.append(comm)
    		i=i+1
    	return cricbuzz_comms

    def extract_line_of_ball(self,commentary):
    	# Define a regex pattern for capturing line and length descriptions
    	pattern = re.compile(r'\b(perfect|good|too)?\s*(full(?:ish|er|-toss|\s toss)?|short(?:ish|er)?|length|slow(?:er|ish)|yorker|pitched up|slot|bouncer|cutter|googly|overpitched|overcook(?:ed|s)|floated|tossed|flighted|banged|cross-seam|half(?: tracker|-tracker)|half(?: volley|-volley))\b.?\b(\s|ball|delivery)?\b', re.IGNORECASE)
    	matches = pattern.findall(commentary)
    	return ' '.join([' '.join(match).strip() for match in matches])

    def extract_length_of_ball(self,commentary):
    	pattern = re.compile(r'\b(on|wide|wide outside|outside|at|in|around|down)\b.?\s*\b(off(?: stump)?|middle|stumps|pads|body|hip|leg|side|leg-side|the stumps)?\b', re.IGNORECASE)
    	matches = pattern.findall(commentary)
    	return ' '.join([' '.join(match).strip() for match in matches])




class PlayerBatHighlightsImageResource(Resource):

	#pbsrObj = PlayerBatStrengthsResource()
	def __init__(self):
		self.tag = "PlayerBatHighlightsImageResource"
		self.pbsrObj = PlayerBatStrengthsResource()

	def get(self, playerId,area):
		comms=[]
		if(area=='fours'):
			cricbuzz_comms = self.pbsrObj.getPlayerFoursScoredData(playerId)
			comms=[cc["text"] for cc in cricbuzz_comms]
		elif(area=='sixes'):
			cricbuzz_comms = self.pbsrObj.getPlayerSixesScoredData(playerId)
			comms=[cc["text"] for cc in cricbuzz_comms]
		img = self.highlight_top_words_in_sentences(comms, num_words=25)
		return send_file(img, mimetype='image/png')

	def highlight_top_words_in_sentences(self,sentences, num_words=25):
		cleaned_sentences=[self.clean_comm_text(x) for x in sentences]
		text = ' '.join(cleaned_sentences)
		stop_words = set(stopwords.words('english'))
		tokens = word_tokenize(text)
		filtered_tokens = [word for word in tokens if word.lower() not in stop_words and re.match(r'\b\w+\b', word)]
		freq_dist = FreqDist(filtered_tokens)
		top_words = freq_dist.most_common(num_words)
		wordcloud = WordCloud(collocations=False, background_color='white').generate_from_frequencies(dict(top_words))
		img = BytesIO()
		plt.figure(figsize=(10, 5))
		plt.imshow(wordcloud, interpolation='nearest')
		plt.axis('off')
		plt.savefig(img, format='png')
		plt.close()
		img.seek(0)
		return img

	def clean_comm_text(self, x, removable_words_list=['delivery','ball','boundary','fielder','runs','fence','man']):
		if(x==None or x==""):
			return ""
		lis = '|'.join(removable_words_list)
		pattern = r'\b(?:' + lis + r')\b'
		clean = re.sub(pattern, '', x)    
		return clean  





