from flask import Blueprint
from flask_restful import Api
from resources.match import MatchResource
from resources.scorecard import ScorecardResource
from resources.player import PlayerResource, FavouritePlayersResource, SearchPlayersResource, PlayerPlayedResource

api_bp = Blueprint('cric/ml/services', __name__)
api = Api(api_bp)

# Route For Match endpoint
api.add_resource(MatchResource,'/matches/<int:id>')
api.add_resource(ScorecardResource,'/scorecards/<int:matchId>')
api.add_resource(PlayerResource,'/players/<int:playerId>')
api.add_resource(PlayerPlayedResource,'/players/<int:playerId>/playedAs/<string:role>')
api.add_resource(FavouritePlayersResource,'/favourites/players')
api.add_resource(SearchPlayersResource,'/search/players/<string:searchString>')



