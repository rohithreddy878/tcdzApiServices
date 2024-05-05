from flask import Blueprint
from flask_restful import Api
from resources.match import MatchResource
from resources.scorecard import ScorecardResource

api_bp = Blueprint('api/v1', __name__)
api = Api(api_bp)

# Route For Match endpoint
api.add_resource(MatchResource,'/matches/<int:id>')
api.add_resource(ScorecardResource,'/scorecards/<int:matchId>')



