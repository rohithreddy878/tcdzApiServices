from flask import Blueprint
from flask_restful import Api
from resources.match import MatchResource, MatchesListPaginatedResource
from resources.scorecard import ScorecardResource
from resources.player import PlayerResource, FavouritePlayersResource, SearchPlayersResource
from resources.player import PlayerPlayedResource, PlayerCareerStatsResource, PlayerTeamsResource
from resources.playerAnalysis import PlayerBatStrengthsResource, PlayerBatHighlightsImageResource
from resources.league import LeagueSeasonsResource, LeagueEventsForSeasonResource

api_bp = Blueprint('cric/ml/services', __name__)
api = Api(api_bp)

# Route For Match endpoint
api.add_resource(MatchResource,'/matches/<int:matchId>')
api.add_resource(ScorecardResource,'/scorecards/<int:matchId>')
api.add_resource(MatchesListPaginatedResource,'/matches/paginated/<int:leagueEventId>')

api.add_resource(PlayerResource,'/players/<int:playerId>')
api.add_resource(PlayerPlayedResource,'/players/<int:playerId>/playedAs')
api.add_resource(FavouritePlayersResource,'/favourites/players')
api.add_resource(SearchPlayersResource,'/search/players/<string:searchString>')
api.add_resource(PlayerCareerStatsResource, '/stats/players/<int:playerId>')
api.add_resource(PlayerTeamsResource, '/teams/players/<int:playerId>')
api.add_resource(PlayerBatStrengthsResource, '/strengths/bat/players/<int:playerId>/<string:area>')
api.add_resource(PlayerBatHighlightsImageResource, '/strengths/bat/highlights/players/<int:playerId>/<string:area>')


api.add_resource(LeagueSeasonsResource, '/leagues/seasons')
api.add_resource(LeagueEventsForSeasonResource, '/leagues/events/<string:season>')








