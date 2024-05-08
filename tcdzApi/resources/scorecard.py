from flask import jsonify, request
from flask_restful import Resource
from model import db, Match, Delivery, Innings, Player
from Constants import BOWLER_CREDITED_WICKET_KINDS
from ast import literal_eval
import json
from util.DTOs import InningsScorecard, BatterScore,BowlerScore 
from typing import List
import time

class ScorecardResource(Resource):
    def __init__(self):
        self.tag = "ScorecardResource"

    def get(self, matchId):
        #innsScList = self.get_match_innings_scorecards_list(matchId)
        #innsScListSer = [sc.to_dict() for sc in innsScList]
        #for local
        with open('./util/619_scorecard.json', 'r') as file: #/Users/rohithreddy/Downloads/cricket_project/git/tcdzApiServices/tcdzApi/util/619_scorecard.json
            j = json.load(file)
        innsScListSer = j.get('data')
        return {'status': 'success', 'data': innsScListSer}, 200
    
    def get_match_innings_scorecards_list(self, mId: int) -> List[InningsScorecard]:
        start_time = time.time()
        isc_list = []
        #print("start_time: ", start_time)
        #match = Match.query.filter_by(match_id=mId).first()  # Assuming match_repo is defined elsewhere
        matchInnsList = Innings.query.filter_by(match_id=mId).all()
        for innings in matchInnsList:
            isc = InningsScorecard()
            isc.match_id = mId
            isc.innings_id = innings.innings_id
            isc.name = innings.team
            isc.index = int(innings.innings_number)

            query_start_time = time.time()
            dels_list = Delivery.query.filter_by(innings_id=innings.innings_id).all()  # Assuming delivery_repo is defined elsewhere
            #print("time take for the delivery query fetch in ms: ", ((time.time()-query_start_time)*1000))
            #print("check the size if u want: ", len(dels_list))
            # Handle BatterScore
            batpos = 1
            #print("starting batting of ",isc.name," at time stamp from start: ", ((time.time()-start_time)*1000)) 
            for deli in dels_list:
                
                isc.runs += deli.runs.total_runs
                isc.extras += deli.runs.extra_runs
                
                if not isc.scorecard_has_batter(deli.batter):  ##sending batter id
                    bs = BatterScore()
                    bs.batter_name = deli.batter_info.common_name if deli.batter_info.common_name else deli.batter_info.name
                    bs.batter_id = deli.batter_info.player_id
                    bs.batting_position = batpos
                    batpos += 1
                    isc.add_batter_score_to_innings(bs)
                
                bs = isc.get_batter_score_from_innings(deli.batter)  ##sending batter id
                if not (deli.extras and deli.extras.wides > 0):
                    bs.balls += 1
                bs.runs += deli.runs.batter_runs
                if deli.runs.batter_runs == 4:
                    bs.fours += 1
                if deli.runs.batter_runs == 6:
                    bs.sixes += 1
                if deli.wicket:
                    isc.wickets += 1
                    if deli.wicket.player_out_info.player_id == bs.batter_id:
                        bs.fill_wicket_details(deli.wicket)
                        bs.out = True
                    else:
                        if not isc.scorecard_has_batter(deli.wicket.player_out):
                            bs2 = BatterScore()
                            bs2.batter_name = deli.wicket.player_out_info.common_name if deli.wicket.player_out_info.common_name else deli.wicket.player_out_info.name
                            bs2.batter_id = deli.wicket.player_out_info.player_id
                            bs2.batting_position = batpos
                            batpos += 1
                            isc.add_batter_score_to_innings(bs2)
                        bs2 = isc.get_batter_score_from_innings(deli.wicket.player_out) ##sending player_out id 
                        bs2.fill_wicket_details(deli.wicket)
                        bs2.out = True         
            print("finished batting innings of ",isc.name," at time stamp from start: ", ((time.time()-start_time)*1000)) 
            # Calculate strike rates for batters
            for bs in isc.batter_scores_list:
                bs.strike_rate = round(100 * bs.runs / bs.balls, 2) if bs.balls != 0 else 0 
            #print("starting bowling of ",isc.name," at time stamp from start: ", ((time.time()-start_time)*1000)) 
            # Handle BowlerScore
            for deli in dels_list:
                if not isc.scorecard_has_bowler(deli.bowler):   ##sending bowler id 
                    bc = BowlerScore()
                    bc.bowler_id = deli.bowler_info.player_id
                    bc.bowler_name = deli.bowler_info.common_name if deli.bowler_info.common_name else deli.bowler_info.name
                    isc.add_bowler_score_to_innings(bc)
                
                bc = isc.get_bowler_score_from_innings(deli.bowler)   ##sending bowler id 
                if not (deli.extras and (deli.extras.noballs > 0 or deli.extras.wides > 0)):
                    bc.balls += 1
                bc.runs += deli.runs.batter_runs
                if deli.extras:
                    bc.runs += deli.extras.wides + deli.extras.noballs
                    bc.wides += deli.extras.wides
                    bc.noballs += deli.extras.noballs
                if deli.wicket and deli.wicket.kind in BOWLER_CREDITED_WICKET_KINDS:
                    bc.wickets += 1
            print("finished bowling innings of ",isc.name," at time stamp from start: ",((time.time()-start_time)*1000))
            # Calculate overs and economies for bowlers
            total_balls = sum(bc.balls for bc in isc.bowler_scores_list)
            total_overs = total_balls // 6 + (total_balls % 6) / 10
            isc.overs = round(total_overs, 2)
            for bc in isc.bowler_scores_list:
                bc.overs = round(bc.balls / 6 + (bc.balls % 6) / 10, 2)
                bc.economy = round(bc.runs / (bc.balls / 6), 2) if bc.balls != 0 else 0
            #print("finished econs of bowling innings of ",isc.name," at time stamp from start: ",((time.time()-start_time)*1000)) 

            isc_list.append(isc)

        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000
        print("scorecards fetch done in ms: ", elapsed_time_ms)
        return isc_list