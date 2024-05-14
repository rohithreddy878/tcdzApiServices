from flask import jsonify, request
from flask_restful import Resource
from ast import literal_eval
import json
from sqlalchemy import text
from typing import List
import time

from util.DTOs import InningsScorecard, BatterScore,BowlerScore 
from model import db, Match, Delivery, Innings, Player, Team
from Constants import BOWLER_CREDITED_WICKET_KINDS, DELIVERIES_FOR_INNINGS_FETCH_QUERY

class ScorecardResource(Resource):
    def __init__(self):
        self.tag = "ScorecardResource"

    def get(self, matchId):
        innsScList = self.get_match_innings_scorecards_list2(matchId)
        innsScListSer = [sc.to_dict() for sc in innsScList]
        # for local
        #with open('./util/619_scorecard.json', 'r') as file: 
        #    j = json.load(file)
        #innsScListSer = j.get('data')
        return {'status': 'success', 'data': innsScListSer}, 200
    
    def get_match_innings_scorecards_list(self, mId: int) -> List[InningsScorecard]:
        start_time = time.time()
        isc_list = []
        #match = Match.query.filter_by(match_id=mId).first()  # Assuming match_repo is defined elsewhere
        matchInnsList = Innings.query.filter_by(match_id=mId).all()
        for innings in matchInnsList:
            isc = InningsScorecard()
            isc.match_id = mId
            isc.innings_id = innings.innings_id
            isc.name = innings.team
            isc.teamDisplayName = innings.team_info.display_name
            isc.index = int(innings.innings_number)

            query_start_time = time.time()
            dels_list = Delivery.query.filter_by(innings_id=innings.innings_id).all()  # Assuming delivery_repo is defined elsewhere
            print("time taken for the delivery query fetch of ",isc.name," in sec: ", ((time.time()-query_start_time)))

            # Handle BatterScore
            batpos = 1
            #print("starting batting of ",isc.name," at time stamp from start: ", ((time.time()-start_time)*1000)) 
            for deli in dels_list:
                s_ti =  time.time()
                isc.runs += deli.runs.total_runs
                isc.extras += deli.runs.extra_runs
                if(dels_list.index(deli)%10==0):
                    print("time taken for runs addition, at ",dels_list.index(deli)," delivery in sec is: ",((time.time()-s_ti))) 
                if not isc.scorecard_has_batter(deli.batter):  ##sending batter id
                    bs = BatterScore()
                    bs.batter_name = deli.batter_info.common_name if deli.batter_info.common_name else deli.batter_info.name
                    bs.batter_id = deli.batter_info.player_id
                    bs.batting_position = batpos
                    batpos += 1
                    isc.add_batter_score_to_innings(bs)
                if(dels_list.index(deli)%10==0):
                    print("time taken for adding new batsman, at ",dels_list.index(deli)," delivery in sec is: ",((time.time()-s_ti))) 
                bs = isc.get_batter_score_from_innings(deli.batter)  ##sending batter id
                if not (deli.extras and deli.extras.wides > 0):
                    bs.balls += 1
                bs.runs += deli.runs.batter_runs
                if deli.runs.batter_runs == 4:
                    bs.fours += 1
                if deli.runs.batter_runs == 6:
                    bs.sixes += 1
                if(dels_list.index(deli)%10==0):
                    print("time taken for batter runs addn, at ",dels_list.index(deli)," delivery in sec is: ",((time.time()-s_ti))) 
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
                if(dels_list.index(deli)%10==0):
                    print("time taken for wicket details addition, at ",dels_list.index(deli)," delivery in sec is: ",((time.time()-s_ti))) 
                if(dels_list.index(deli)%10==0):
                    print("time taken for each deliv bat sc, at ",dels_list.index(deli)," delivery in sec is: ",((time.time()-s_ti)))        
            print("finished batting innings of ",isc.name," in sec from start: ", ((time.time()-start_time))) 
 
            # Handle BowlerScore
            for deli in dels_list:
                s_ti =  time.time()
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
                #if(dels_list.index(deli)%10==0):
                    #print("time taken for each deliv BOWL sc, at ",dels_list.index(deli)," delivery in sec is: ",((time.time()-s_ti)))   
            print("finished bowling innings of ",isc.name," in sec from start: ",((time.time()-start_time)))


            # Calculate overs and economies for bowlers
            total_balls = sum(bc.balls for bc in isc.bowler_scores_list)
            total_overs = total_balls // 6 + (total_balls % 6) / 10
            isc.overs = round(total_overs, 2)
            #print("finished econs of bowling innings of ",isc.name," at time stamp from start: ",((time.time()-start_time)*1000))

            isc_list.append(isc)

        elapsed_time_ms = (time.time() - start_time) * 1000
        print("scorecards fetch done in ms: ", elapsed_time_ms)
        return isc_list

    def get_match_innings_scorecards_list2(self, mId: int):
        isc_list = []
        matchInnsQuery = text("SELECT * from cricket.innings WHERE match_id= :matchId ORDER BY innings_number ASC")
        matchInnsQueryRes = db.session.execute(matchInnsQuery, {"matchId": mId})
        res = matchInnsQueryRes.mappings().all()
        for inn_row in res:
            #print("inn: ", inn_row)
            isc = InningsScorecard()
            isc.match_id = inn_row.match_id
            isc.innings_id = inn_row.innings_id
            isc.name = inn_row.team
            teamObj = Team.query.filter_by(name=inn_row.team).first()
            isc.teamDisplayName = teamObj.display_name #take care
            isc.index = int(inn_row.innings_number)

            delsFetchQuery = text(DELIVERIES_FOR_INNINGS_FETCH_QUERY)
            delsFetchQueryRes = db.session.execute(delsFetchQuery, {"inningsIdParam": inn_row.innings_id})
            delsList = delsFetchQueryRes.mappings().all()
            #print("delsList size and first element: ", len(delsList), "---", delsList[0])
            #Handle batter score
            batpos=1
            for deli in delsList:
                isc.runs += deli.total_runs
                isc.extras += deli.extra_runs

                if not isc.scorecard_has_batter(deli.batter):  ##sending batter id
                    bs = BatterScore()
                    bs.batter_name = self.getPlayerNameUsingId(deli.batter)
                    bs.batter_id = deli.batter
                    bs.batting_position = batpos
                    batpos += 1
                    isc.add_batter_score_to_innings(bs)

                bs = isc.get_batter_score_from_innings(deli.batter)  ##sending batter id
                if not (deli.extras_id and deli.wides > 0):
                    bs.balls += 1
                bs.runs += deli.batter_runs
                if deli.batter_runs == 4:
                    bs.fours += 1
                if deli.batter_runs == 6:
                    bs.sixes += 1
                if deli.wicket_id is not None:
                    isc.wickets += 1
                    k=deli.kind
                    bn=self.getPlayerNameUsingId(deli.bowler)
                    f1n=self.getPlayerNameUsingId(deli.fielder1) if deli.fielder1!=None else None
                    f2n=self.getPlayerNameUsingId(deli.fielder2) if deli.fielder2!=None else None
                    if deli.player_out == bs.batter_id:
                        bs.fill_wicket_details2(k,bn,f1n,f2n)
                        bs.out = True
                    else:
                        if not isc.scorecard_has_batter(deli.player_out):  ##sending batter id
                            bs2 = BatterScore()
                            p2 = Player.query.filter_by(player_id=deli.player_out).first()
                            bs2.batter_name = p2.common_name if p2.common_name else p2.name
                            bs2.batter_id = p2.player_id
                            bs2.batting_position = batpos
                            batpos += 1
                            isc.add_batter_score_to_innings(bs2)
                        bs2 = isc.get_batter_score_from_innings(deli.player_out) ##sending player_out id 
                        bs2.fill_wicket_details2(k,bn,f1n,f2n)
                        bs2.out = True  

            # Handle BowlerScore
            for deli in delsList:
                if not isc.scorecard_has_bowler(deli.bowler):   ##sending bowler id 
                    bc = BowlerScore()
                    bc.bowler_id = deli.bowler
                    bc.bowler_name = self.getPlayerNameUsingId(deli.bowler)
                    isc.add_bowler_score_to_innings(bc)
                
                bc = isc.get_bowler_score_from_innings(deli.bowler)   ##sending bowler id 
                if not (deli.extras_id and (deli.noballs > 0 or deli.wides > 0)):
                    bc.balls += 1
                bc.runs += deli.batter_runs
                if deli.extras_id:
                    bc.runs += (deli.wides + deli.noballs)
                    bc.wides += deli.wides if deli.wides else 0
                    bc.noballs += deli.noballs if deli.noballs else 0
                if deli.wicket_id and deli.kind in BOWLER_CREDITED_WICKET_KINDS:
                    bc.wickets += 1

            total_balls = sum(bc.balls for bc in isc.bowler_scores_list)
            total_overs = total_balls // 6 + (total_balls % 6) / 10
            isc.overs = round(total_overs, 2)

            isc_list.append(isc)


        return isc_list


    def getPlayerNameUsingId(self, pId):
        p = Player.query.filter_by(player_id=pId).with_entities(Player.name, Player.common_name).first()
        name = p.common_name if p.common_name else p.name
        return name






