class BatterScore:
    def __init__(self):
        self.batter_name = ""
        self.batter_id = None
        self.batting_position = 0
        self.runs = 0
        self.balls = 0
        self.fours = 0
        self.sixes = 0
        #self.strike_rate = 0
        self.out = False
        self.wicket_bowler_name = ""
        self.wicket_fielder1_name = ""
        self.wicket_fielder2_name = ""
        self.wicket_kind = ""

    def to_dict(self):
        return {
            'batterName': self.batter_name,
            'batterId': self.batter_id,
            'battingPosition': self.batting_position,
            'runs': self.runs,
            'balls': self.balls,
            'fours': self.fours,
            'sixes': self.sixes,
            #'strikeRate': self.strike_rate,
            'out': self.out,
            'wicketBowlerName': self.wicket_bowler_name,
            'wicketFielder1Name': self.wicket_fielder1_name,
            'wicketFielder2Name': self.wicket_fielder2_name,
            'wicketKind': self.wicket_kind
        }

    def fill_wicket_details(self, w):
        self.wicket_kind = w.kind
        self.wicket_bowler_name = w.bowler_info.common_name if w.bowler_info.common_name else w.bowler_info.name
        if(w.fielder1_info):
            self.wicket_fielder1_name = w.fielder1_info.common_name if w.fielder1_info.common_name else w.fielder1_info.name
        if(w.fielder2_info):
            self.wicket_fielder2_name = w.fielder2_info.common_name if w.fielder2_info.common_name else w.fielder2_info.name

    def fill_wicket_details2(self, k,bn,f1n,f2n):
        self.wicket_kind = k
        self.wicket_bowler_name = bn
        if(f1n != '' and f1n != None):
            self.wicket_fielder1_name = f1n
        if(f2n != '' and f2n != None):
         self.wicket_fielder2_name = f2n



#--------------------------------------

class BowlerScore:
    def __init__(self):
        self.bowler_id = None
        self.bowler_name = ""
        #self.overs = 0
        self.balls = 0
        self.maidens = 0
        self.runs = 0
        self.wickets = 0
        self.noballs = 0
        self.wides = 0
        #self.economy = 0

    def to_dict(self):
        return {
            'bowlerId': self.bowler_id,
            'bowlerName': self.bowler_name,
            #'overs': self.overs,
            'balls': self.balls,
            #'maidens': self.maidens,
            'runs': self.runs,
            'wickets': self.wickets,
            'noballs': self.noballs,
            'wides': self.wides,
            #'economy': self.economy
        }
    

#-----------------------------------------

class InningsScorecard:
    def __init__(self):
        self.match_id = None
        self.innings_id = None
        self.name = ""
        self.index = 0
        self.runs = 0
        self.overs = 0
        self.wickets = 0
        self.extras = 0
        self.teamDisplayName = ""
        self.batter_scores_list = []
        self.bowler_scores_list = []

    def add_batter_score_to_innings(self, bs):
        self.batter_scores_list.append(bs)

    def add_bowler_score_to_innings(self, bc):
        self.bowler_scores_list.append(bc)

    def get_batter_score_from_innings(self, id):
        for batter_score in self.batter_scores_list:
            if batter_score.batter_id == id:
                return batter_score
        return None

    def get_bowler_score_from_innings(self, id):
        for bowler_score in self.bowler_scores_list:
            if bowler_score.bowler_id == id:
                return bowler_score
        return None

    def scorecard_has_batter(self, batId):
        return any(bs.batter_id == batId for bs in self.batter_scores_list)

    def scorecard_has_bowler(self, bowlId):
        return any(bc.bowler_id == bowlId for bc in self.bowler_scores_list)
    
    def to_dict(self):
        return {
            'matchId': self.match_id,
            'inningsId': self.innings_id,
            'teamName': self.name,
            'index': self.index,
            'runs': self.runs,
            'overs': self.overs,
            'wickets': self.wickets,
            'extras': self.extras,
            'batterScoresList': [bs.to_dict() for bs in self.batter_scores_list],
            'bowlerScoresList': [bc.to_dict() for bc in self.bowler_scores_list],
            'teamDisplayName': self.teamDisplayName
        }