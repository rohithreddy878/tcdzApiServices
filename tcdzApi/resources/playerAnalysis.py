from flask import send_file
from sqlalchemy import text
import re
from io import BytesIO
from collections import Counter

from model import db
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
nlp = spacy.load('en_core_web_sm')

# Ensure the necessary NLTK data is available
nltk.download('punkt')
nltk.download('stopwords')

#Ml model inferencing
from flask_restful import Resource
from transformers import AutoTokenizer
import torch
from ml.multiTaskModel import MultiTaskModel
import pickle


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

class BatsmanStrengthsResource(Resource):
    def __init__(self):
        self.tag = "BatsmanStrengthsResource"

    def get(self, playerId):
        strengths = {}

        comms = self.getPlayerRunsComms(playerId, 4)
        #print("no of fours: ", len(comms))
        li, le = self.getLengthsandLinesProbabibilitiesMapsFromCommsList(comms)
        strengths["fours_lines_counter"] = Counter(li)
        strengths["fours_lengths_counter"] = Counter(le)

        comms = self.getPlayerRunsComms(playerId, 6)
        li, sixes_lengths = self.getLengthsandLinesProbabibilitiesMapsFromCommsList(comms)
        strengths["sixes_lines_counter"] = Counter(li)
        strengths["sixes_lengths_counter"] = Counter(le)

        comms = self.getPlayerOutsComms(playerId)
        li, le = self.getLengthsandLinesProbabibilitiesMapsFromCommsList(comms)
        strengths["outs_lines_counter"] = Counter(li)
        strengths["outs_lengths_counter"] = Counter(le)

        return {'status': 'success', 'data': strengths}, 200

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

    def getLengthsandLinesProbabibilitiesMapsFromCommsList(self, comms_list):
        # Load the encoders
        with open('static/ml_models/linelengthpredictor/line_encoder.pkl', 'rb') as f:
            line_encoder = pickle.load(f)
        with open('static/ml_models/linelengthpredictor/length_encoder.pkl', 'rb') as f:
            length_encoder = pickle.load(f)

        num_lines = len(line_encoder.classes_)
        num_lengths = len(length_encoder.classes_)
        ## print(num_lines, num_lengths)

        # Initialize and load model weights
        tokenizer = AutoTokenizer.from_pretrained("google/mobilebert-uncased")
        model = MultiTaskModel("google/mobilebert-uncased", num_line_labels=num_lines, num_length_labels=num_lengths)
        model.load_state_dict(torch.load("static/ml_models/linelengthpredictor/linelengthpredictor_weights.pth", map_location="cpu"))
        model.eval()

        lines = []
        lengths = []
        for c in comms_list:
            li, le = self.predict_line_length(c,model, tokenizer, line_encoder, length_encoder)
            if li is None or le is None:
                continue
            lines.append(li)
            lengths.append(le)
        return lines, lengths

    def predict_line_length(self, c, model, tokenizer, line_encoder, length_encoder):
        if not c:
            return None, None
        inputs = tokenizer(c, return_tensors="pt", padding=True, truncation=True, max_length=512)
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        #model.eval()
        with torch.no_grad():
            out = model(input_ids=input_ids, attention_mask=attention_mask)

        pred_line_index = torch.argmax(out["logits_line"], dim=-1).item()
        pred_length_index = torch.argmax(out["logits_length"], dim=-1).item()

        pred_line = line_encoder.inverse_transform([pred_line_index])[0]
        pred_length = length_encoder.inverse_transform([pred_length_index])[0]

        return pred_line, pred_length


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


