from flask import jsonify, request
from ast import literal_eval
from sqlalchemy import desc, func
import json
from flask_restful import Resource

from model import db, Match, Delivery, Innings, Player
from Constants import BOWLER_CREDITED_WICKET_KINDS

class MatchResource(Resource):
    def __init__(self):
        self.tag = "MatchResource"

    def get(self, matchId):
        m = Match.query.filter_by(match_id=matchId).first()
        res_json = m.to_dict()
        return {'status': 'success', 'data': res_json}, 200


class MatchesListPaginatedResource(Resource):
    def __init__(self):
        self.tag = "MatchesListPaginatedResource"

    def get(self, leagueEventId):
        page_num = request.args.get('pageNo', default=1, type=int) 
        page_size = request.args.get('pageSize', default=10, type=int)
        offset = (page_num - 1) * page_size

        totalCount = Match.query.filter_by(league_event_id=leagueEventId).count()
        print("totalCount: ", totalCount)
        matchesList = Match.query.filter_by(league_event_id=leagueEventId) \
                     .order_by(desc(Match.date), desc(Match.event_stage)) \
                     .offset(offset) \
                     .limit(page_size) \
                     .all()
        matchesListDicts = [m.to_dict_basic() for m in matchesList]
        res={
            'matchesList':matchesListDicts,
            'pageNo':page_num,
            'pageSize':page_size,
            'totalResults':totalCount
        }
        return {'status': 'success', 'data': res}, 200




