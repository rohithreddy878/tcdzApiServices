from flask import send_file
from flask_restful import Resource
from sqlalchemy import text
import re
from io import BytesIO

from model import db, Player
import Constants

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import spacy
import numpy as np
nlp = spacy.load('en_core_web_sm')

# Ensure the necessary NLTK data is available
nltk.download('punkt')
nltk.download('stopwords')


class PlayerBatStrengthsResource(Resource):
    def __init__(self):
        self.tag = "PlayerBatStrengthsResource"

    def get(self, playerId, area):
        cricbuzz_comms = []
        if area == 'fours':
            cricbuzz_comms = self.getPlayerFoursScoredData(playerId)
        elif area == 'sixes':
            cricbuzz_comms = self.getPlayerSixesScoredData(playerId)
        elif area == 'outs':
            cricbuzz_comms = self.getPlayerGotOutData(playerId)

        return {'status': 'success', 'data': cricbuzz_comms}, 200

    def getPlayerFoursScoredData(self, playerId):
        query = text(Constants.PLAYER_RUNS_SCORED_COMMS_QUERY)
        queryRes = db.session.execute(query, {"playerIdParam": playerId, "runsParam": 4})
        queryResMaps = queryRes.mappings().all()
        #print("queryResMaps: ",queryResMaps)
        cricbuzz_comms = []
        i = 1
        for row in queryResMaps:
            c = row["cricbuzz_commentary"]
            length = self.extract_line_of_ball(c) if c else ""
            line = self.extract_length_of_ball(c) if c else ""
            comm = {'i': i, 'text': c, 'line': line, 'length': length}
            i = i + 1
            cricbuzz_comms.append(comm)
        return cricbuzz_comms

    def getPlayerSixesScoredData(self, playerId):
        query = text(Constants.PLAYER_RUNS_SCORED_COMMS_QUERY)
        queryRes = db.session.execute(query, {"playerIdParam": playerId, 'runsParam': 6}).mappings().all()
        cricbuzz_comms = []
        i = 1
        for row in queryRes:
            c = row["cricbuzz_commentary"]
            length = self.extract_line_of_ball(c) if c else ""
            line = self.extract_length_of_ball(c) if c else ""
            comm = {'i': i, 'text': c, 'line': line, 'length': length}
            cricbuzz_comms.append(comm)
            i = i + 1
        return cricbuzz_comms

    def getPlayerGotOutData(self, playerId):
        query = text(Constants.PLAYER_GOT_OUT_COMMS_QUERY)
        queryRes = db.session.execute(query, {"playerIdParam": playerId}).mappings().all()
        cricbuzz_comms = []
        i = 1
        for row in queryRes:
            c = row["cricbuzz_commentary"]
            length = self.extract_line_of_ball(c) if c else ""
            line = self.extract_length_of_ball(c) if c else ""
            comm = {'i': i, 'text': c, 'line': line, 'length': length}
            cricbuzz_comms.append(comm)
            i = i + 1
        return cricbuzz_comms

    @staticmethod
    def extract_line_of_ball(commentary):
        # Define a regex pattern for capturing line and length descriptions
        pattern = re.compile(
            r'\b(perfect|good|too)?\s*(full(?:ish|er|-toss|\s toss)?|short(?:ish|er)?|length|slow(?:er|ish)|yorker|pitched up|slot|bouncer|cutter|googly|overpitched|overcook(?:ed|s)|floated|tossed|flighted|banged|cross-seam|half(?: tracker|-tracker)|half(?: volley|-volley))\b.?\b(\s|ball|delivery)?\b',
            re.IGNORECASE)
        matches = pattern.findall(commentary)
        return ' '.join([' '.join(match).strip() for match in matches])

    @staticmethod
    def extract_length_of_ball(commentary):
        pattern = re.compile(
            r'\b(on|wide|wide outside|outside|at|in|around|down)\b.?\s*\b(off(?: stump)?|middle|stumps|pads|body|hip|leg|side|leg-side|the stumps)?\b',
            re.IGNORECASE)
        matches = pattern.findall(commentary)
        return ' '.join([' '.join(match).strip() for match in matches])

class BatsmenStrengthsResource(Resource):
    def __init__(self):
        self.tag = "BatsmenStrengthsResource"

    def get(self, playerId):
        strengths = {}
        fours_comms = self.getPlayerRunsComms(playerId, 4)
        sixes_comms = self.getPlayerRunsComms(playerId, 6)
        outs_comms = self.getPlayerOutsComms(playerId)
        return {'status': 'success', 'data': strengths}, 200

    def getLengthsandLinesProbabibilitiesMapsFromCommsList(self, comms_list):
        return []

    def getPlayerRunsComms(self, playerId, runsParam):
        query = text(Constants.PLAYER_RUNS_SCORED_COMMS_QUERY)
        queryRes = db.session.execute(query, {"playerIdParam": playerId, "runsParam": runsParam})
        queryResMaps = queryRes.mappings().all()
        runs_comms = self.mapCommsQueryResultsToList(queryResMaps)
        return runs_comms

    def getPlayerOutsComms(self, playerId):
        query = text(Constants.PLAYER_GOT_OUT_COMMS_QUERY)
        queryResMap = db.session.execute(query, {"playerIdParam": playerId}).mappings().all()
        outs_comms = self.mapCommsQueryResultsToList(queryResMap)
        return outs_comms

    def mapCommsQueryResultsToList(self, queryResMap):
        comms_list = []
        for row in queryResMap:
            c = row["cricbuzz_commentary"]
            comms_list.append(c)
        return comms_list



class PlayerBatHighlightsImageResource(Resource):
    def __init__(self):
        self.tag = "PlayerBatHighlightsImageResource"
        self.pbsrObj = PlayerBatStrengthsResource()

    def get(self, playerId, area):
        removable_words= Constants.BATTING_HIGHLIGHTS_REMOVABLE_WORDS
        comms = []
        if area == 'fours':
            cricbuzz_comms = self.pbsrObj.getPlayerFoursScoredData(playerId)
            comms = [cc["text"] for cc in cricbuzz_comms]
        elif area == 'sixes':
            cricbuzz_comms = self.pbsrObj.getPlayerSixesScoredData(playerId)
            comms = [cc["text"] for cc in cricbuzz_comms]
        img = self.highlight_top_words_in_sentences(comms, removable_words, num_words=25)
        return send_file(img, mimetype='image/png')

    def highlight_top_words_in_sentences(self, sentences,removable_words, num_words=25):
        names_removed_sentences=[self.remove_proper_nouns(x) for x in sentences if x is not None]
        cleaned_sentences = [self.clean_comm_text(x,removable_words) for x in names_removed_sentences]
        comm_text = ' '.join(cleaned_sentences)
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(comm_text)
        filtered_tokens = [word for word in tokens if word.lower() not in stop_words and re.match(r'\b\w+\b', word)]
        freq_dist = FreqDist(filtered_tokens)
        top_words = freq_dist.most_common(num_words)

        wordcloud = WordCloud(collocations=False, background_color='white').generate_from_frequencies(dict(top_words))
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='nearest')
        plt.axis('off')
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0.2)
        plt.close()
        img.seek(0)
        return img

    @staticmethod
    def clean_comm_text(x,removable_words_list):
        if x is None or x == "":
            return ""
        x = ' '.join(word for word in x.split() if len(word) >= 3)
        lis = '|'.join(removable_words_list)
        pattern = r'\b(?:' + lis + r')\b'
        clean = re.sub(pattern, '', x)
        return clean

    def remove_proper_nouns(self, text):
        doc = nlp(text)
        cleaned_text = ' '.join([token.text for token in doc if token.pos_ != 'PROPN'])
        return cleaned_text


