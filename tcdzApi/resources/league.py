from flask_restful import Resource
from sqlalchemy import text

from model import db, LeagueEvent

class LeagueSeasonsResource(Resource):
    def __init__(self):
        self.tag = "LeagueSeasonsResource"

    def get(self):
        query = text("SELECT distinct(l.season) from cricket.league_events l where l.name='Indian Premier League' order by l.season DESC")
        result = db.session.execute(query)
        seasons =  result.mappings().all()
        seasonsList = []
        for s in seasons:
        	 seasonsList.append(s['season'])
        return {'status': 'success', 'data':seasonsList}, 200


class LeagueEventsForSeasonResource(Resource):
    def __init__(self):
        self.tag = "LeagueEventsForSeasonResource"

    def get(self,season):
        query = text("SELECT l.league_event_id from cricket.league_events l where l.season=:seasonString and l.name='Indian Premier League' order by l.league_event_id DESC")
        result = db.session.execute(query, {"seasonString": season})
        resultMap =  result.mappings().all()
        leIdsList = []
        for lId in resultMap:
        	leIdsList.append(lId['league_event_id'])
        lesRes = LeagueEvent.query.filter(LeagueEvent.league_event_id.in_(leIdsList)).all()
        league_events_data = [leagueEvent.to_dict() for leagueEvent in lesRes]

        return {'status': 'success', 'data':league_events_data}, 200











