from flask import jsonify, request
from flask_restful import Resource
from model import db, Match, Delivery, Innings, Player
from Constants import BOWLER_CREDITED_WICKET_KINDS
from ast import literal_eval
import json

class MatchResource(Resource):
    def __init__(self):
        self.tag = "MatchResource"

    def get(self, id):
        print("yeah yeah yeah id is: ",id)
        m = Match.query.filter_by(match_id=id).first()
        res_json = m.to_dict()
        print("res is-------------------------------------------------------------",res_json)
        return {'status': 'success', 'data': res_json}, 200




