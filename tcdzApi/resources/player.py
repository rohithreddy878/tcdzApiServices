from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy import or_, text
from ast import literal_eval
import re
import json

from model import db, Match, Delivery, Innings, Player, Team
from Constants import BOWLER_CREDITED_WICKET_KINDS
from Constants import  FAVOURITE_BATSMEN_LIST,FAVOURITE_BOWLERS_LIST,FAVOURITE_ALLROUNDERS_LIST
import Constants


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
        nameLike = re.escape(searchString.upper())  #'%'+searchString.upper()+'%'
        searchNameParam = "%"+nameLike+"%"
        query = text(Constants.PLAYERS_SEARCH_QUERY)
        result = db.session.execute(query, {"searchNameParam": searchNameParam})
        # Check if the result is empty
        if result.rowcount == 0:
            return {'status': 'failure', 'message': 'No players found'}, 404
        playerRows =  result.mappings().all()
        playersList = [Player.from_row_to_obj(row) for row in playerRows]
        return {'status': 'success', 'data':playersList}, 200

class PlayerTeamsResource(Resource):
    def __init__(self):
        self.tag = "PlayerTeamsResource"

    def get(self,playerId):
        teamsQuery = text(Constants.PLAYER_PLAYED_TEAMS_QUERY)
        teamsQueryRes = db.session.execute(teamsQuery, {"playerIdParam": playerId}).mappings().all()
        teamsListJson = [(Team.query.filter_by(name=t.played_team).first()).to_dict() for t in teamsQueryRes]
        return {'status': 'success', 'data':teamsListJson}, 200


class PlayerCareerStatsResource(Resource):
    def __init__(self):
        self.tag = "PlayerCareerStatsResource"

    def get(self,playerId):
        stats = {}
        stats['totalMatches']=self.getQueryResultForPlayerStat(Constants.PLAYER_TOTAL_IPL_MATCHES_PLAYED,playerId);
        stats['inningsBatted']=self.getQueryResultForPlayerStat(Constants.PLAYER_INNINGS_BATTED_QUERY,playerId);
        stats['inningsBowled']=self.getQueryResultForPlayerStat(Constants.PLAYER_INNINGS_BOWLED_QUERY,playerId);
        
        runs=self.getQueryResultForPlayerStat(Constants.BATTER_RUNS_SCORED_QUERY,playerId)
        stats['runsScored']=float(runs) if runs else 0
        
        stats['ballsFaced']=self.getQueryResultForPlayerStat(Constants.BATTER_BALLS_FACED_QUERY,playerId);
        stats['4s']=self.getQueryResultForPlayerStat(Constants.BATTER_FOURS_SCORED_QUERY,playerId);
        stats['6s']=self.getQueryResultForPlayerStat(Constants.BATTER_SIXES_SCORED_QUERY,playerId);
        outs=self.getQueryResultForPlayerStat(Constants.BATTER_NUMBER_OF_OUTS_QUERY,playerId);
        stats['notOuts']=stats['inningsBatted']-outs;
        
        high_score = self.getQueryResultForPlayerStat(Constants.BATTER_HIGHEST_SCORE_QUERY, playerId)
        stats['highestScore'] = float(high_score) if high_score else 0
        
        stats['100s']=self.getQueryResultForPlayerStatTwoParams(Constants.BATTER_LANDMARK_SCORES_QUERY,playerId,100)
        stats['50s']=self.getQueryResultForPlayerStatTwoParams(Constants.BATTER_LANDMARK_SCORES_QUERY,playerId,50)
        stats['30s']=self.getQueryResultForPlayerStatTwoParams(Constants.BATTER_LANDMARK_SCORES_QUERY,playerId,30)

        stats['ballsBowled']=self.getQueryResultForPlayerStat(Constants.BOWLER_BALLS_BOWLED_QUERY, playerId)

        bw_all_runs=self.getQueryResultForPlayerStat(Constants.BOWLER_ALL_RUNS_CONCEDED_QUERY, playerId)
        bw_all_runs=float(bw_all_runs) if bw_all_runs else 0
        bw_byes_runs=self.getQueryResultForPlayerStat(Constants.BOWLER_BYES_CONCEDED_QUERY, playerId)
        bw_byes_runs=float(bw_byes_runs) if bw_byes_runs else 0
        
        stats['runsConceded']=bw_all_runs-bw_byes_runs

        stats['wickets']=self.getQueryResultForPlayerStat(Constants.BOWLER_WICKETS_TAKEN_QUERY,playerId)
        stats['3wHauls']=self.getQueryResultForPlayerStatTwoParams(Constants.BOWLER_LANDMARK_WICKETS_QUERY,playerId,3)
        stats['4wHauls']=self.getQueryResultForPlayerStatTwoParams(Constants.BOWLER_LANDMARK_WICKETS_QUERY,playerId,4)
            

        print("stats- ",stats)

        return {'status': 'success', 'data':stats}, 200

    def getQueryResultForPlayerStat(self, queryString, playerId):
        query = text(queryString)
        queryRes = db.session.execute(query, {"playerIdParam": playerId})
        count = queryRes.scalar()
        return count

    def getQueryResultForPlayerStatTwoParams(self, queryString, playerId,landmark):
        query = text(queryString)
        queryRes = db.session.execute(query, {"playerIdParam": playerId, "landmarkParam":landmark})
        count = queryRes.scalar()
        return count


















