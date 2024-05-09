from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy import or_, text
from ast import literal_eval
import re
import json

from model import db, Match, Delivery, Innings, Player
from Constants import BOWLER_CREDITED_WICKET_KINDS
from Constants import  FAVOURITE_BATSMEN_LIST,FAVOURITE_BOWLERS_LIST,FAVOURITE_ALLROUNDERS_LIST


class PlayerResource(Resource):
    def __init__(self):
        self.tag = "PlayerResource"

    def get(self, playerId):
        pl = Player.query.filter_by(player_id=playerId).first()
        res_json = pl.to_dict()
        return {'status': 'success', 'data': res_json}, 200

class PlayerPlayedResource(Resource):
    def __init__(self):
        self.tag = "PlayerPlayedResource"

    def get(self, playerId, role):
        count = 0
        if(role=='batter'):
             query = text("SELECT count(*) from cricket.deliveries WHERE batter= :playerId")
        elif(role=='bowler'):
             query = text("SELECT count(*) from cricket.deliveries WHERE bowler= :playerId")        
        result = db.session.execute(query, {"playerId": playerId})
        res = result.mappings().all()
        countRes = res[0].count 
        return {'status': 'success', 'data': {"count":countRes}}, 200

class FavouritePlayersResource(Resource):
    def __init__(self):
        self.tag = "FavouritePlayersResource"

    def get(self):
        favourite_players = []
        for player_list in [FAVOURITE_BATSMEN_LIST,FAVOURITE_BOWLERS_LIST,FAVOURITE_ALLROUNDERS_LIST]:
            favourite_players.extend(player_list)
        fav_players = Player.query.filter(Player.common_name.in_(favourite_players)).all()
        fav_players_data = [player.to_dict() for player in fav_players]
        return {'status': 'success', 'data': fav_players_data}, 200


class SearchPlayersResource(Resource):
    def __init__(self):
        self.tag = "SearchPlayersResource"

    def get(self,searchString):
        nameLike = '\\b' + re.escape(searchString.upper()) + '\\b'  #'%'+searchString.upper()+'%'
        query = text("SELECT * from cricket.players WHERE UPPER(name) ~ :nameLike OR UPPER(common_name) ~ :nameLike")
        result = db.session.execute(query, {"nameLike": nameLike})
        # Check if the result is empty
        if result.rowcount == 0:
            return {'status': 'failure', 'message': 'No players found'}, 404
        playerRows =  result.mappings().all()
        playersList = [Player.from_row_to_obj(row) for row in playerRows]
        return {'status': 'success', 'data':playersList}, 200







