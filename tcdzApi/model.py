from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence

db = SQLAlchemy()

class Team(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'schema': 'cricket'}

    team_seq = Sequence('CRIC_TEAMS_S', metadata=db.metadata)
    team_id = db.Column(db.BigInteger, primary_key=True, server_default=team_seq.next_value())
    
    name = db.Column(db.String(200), nullable=False, unique=True)
    type = db.Column(db.String(100), nullable=False)
    primary_colour = db.Column(db.String(10), nullable=True)
    secondary_colour = db.Column(db.String(10), nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    display_name = db.Column(db.String(20), nullable=False)
    old_names = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'teamId': self.team_id,
            'name': self.name,
            'type': self.type,
            'gender': self.gender,
            'displayName': self.display_name,
            'oldNames': self.old_names,
            'primaryColour':self.primary_colour,
            'secondaryColour':self.secondary_colour
        }

    @staticmethod
    def from_row_to_obj(row):
        return {
            'teamId': row.team_id,
            'name': row.name,
            'type': row.type,
            'gender': row.gender,
            'displayName': row.display_name,
            'oldNames': row.old_names,
            'primaryColour':row.primary_colour,
            'secondaryColour':row.secondary_colour
        }

    def __repr__(self):
        return f"<Team(team_id={self.team_id}, name={self.name}, type={self.type}, gender={self.gender}, display_name={self.display_name}, old_names={self.old_names})>"


class Player(db.Model):
    __tablename__ = 'players'
    __table_args__ = {'schema': 'cricket'}

    player_seq = Sequence('CRIC_PLAYERS_S', metadata=db.metadata)
    player_id = db.Column(db.BigInteger, primary_key=True, server_default=player_seq.next_value())

    name = db.Column(db.String(200), nullable=False)
    player_role = db.Column(db.String(100))
    country = db.Column(db.String(50))
    bat_style = db.Column(db.String(100))
    bowl_style = db.Column(db.String(100))
    cricsheet_id = db.Column(db.String(20), unique=True)
    cricinfo_id = db.Column(db.String(20), unique=True)
    cricsheet_name = db.Column(db.String(200))
    common_name = db.Column(db.String(100))
    photo_url = db.Column(db.String(500))

    def to_dict(self):
        return {
            'playerId': self.player_id,
            'name': self.name,
            'role': self.player_role,
            'country': self.country,
            'batStyle': self.bat_style,
            'bowlStyle': self.bowl_style,
            #'cricsheetId': self.cricsheet_id,
            #'cricinfoId': self.cricinfo_id,
            'cricsheetName': self.cricsheet_name,
            'commonName': self.common_name,
            'photoUrl': self.photo_url,
        }

    @staticmethod
    def from_row_to_obj(row):
        return {
            'playerId': row.player_id,
            'name': row.name,
            'role': row.player_role,
            'country': row.country,
            'batStyle': row.bat_style,
            'bowlStyle': row.bowl_style,
            #'cricsheetId': self.cricsheet_id,
            #'cricinfoId': self.cricinfo_id,
            'cricsheetName': row.cricsheet_name,
            'commonName': row.common_name,
            'photoUrl': row.photo_url,
        }

    def __repr__(self):
        return f'<Player id={self.player_id}, name={self.name}, player_role={self.player_role}, country={self.country}>'


class League(db.Model):
    __tablename__ = 'leagues'
    __table_args__ = {'schema': 'cricket'}

    league_seq = Sequence('CRIC_LEAGUES_S', metadata=db.metadata)
    league_id = db.Column(db.BigInteger, primary_key=True, server_default=league_seq.next_value())
    
    name = db.Column(db.String(200), nullable=False)
    game_format = db.Column(db.String(25), nullable=False)

    def to_dict(self):
        return {
            'leagueId': self.league_id,
            'name': self.name,
            'format': self.game_format
        }

    def __repr__(self):
        return f'<League id={self.league_id}, name={self.name}, format={self.game_format}>'


class LeagueEvent(db.Model):
    __tablename__ = 'league_events'
    __table_args__ = {'schema': 'cricket'}

    league_event_seq = Sequence('CRIC_LEAGUE_EVENTS_S', metadata=db.metadata)
    league_event_id = db.Column(db.BigInteger, primary_key=True, server_default=league_event_seq.next_value())
    
    name = db.Column(db.String(200), nullable=False)
    match_type = db.Column(db.String(10), nullable=False)
    winner_team = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'))
    man_of_series_1 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    man_of_series_2 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    season = db.Column(db.String(10))

    league_id = db.Column(db.Integer, db.ForeignKey('cricket.leagues.league_id'), nullable=False)
    league = db.relationship('League',uselist=False)

    man_of_series_1_info =  db.relationship('Player', uselist=False, foreign_keys=[man_of_series_1])   
    man_of_series_2_info =  db.relationship('Player', uselist=False, foreign_keys=[man_of_series_2])   
    winner_team_info = db.relationship('Team', uselist=False, foreign_keys=[winner_team])  

    def to_dict(self):
        return {
            'leagueEventId': self.league_event_id,
            'name': self.name,
            'matchType': self.match_type,
            'winnerTeam': self.winner_team_info.to_dict() if self.winner_team_info else None,
            'manOfTheSeries1':  self.man_of_series_1_info.to_dict() if self.man_of_series_1_info else None,
            'manOfTheSeries2':  self.man_of_series_2_info.to_dict() if self.man_of_series_2_info else None,
            'season': self.season,
            #'leagueId': self.league_id,
            'league': self.league.to_dict() if self.league else None
        }

    def __repr__(self):
        return f'<LeagueEvent id={self.league_event_id}, name={self.name}, match_type={self.match_type}, season={self.season}>'


class Match(db.Model):
    __tablename__ = 'matches'
    __table_args__ = {'schema': 'cricket'}
    
    match_seq = Sequence('CRIC_MATCHES_S', metadata=db.metadata)
    match_id = db.Column(db.BigInteger, primary_key=True, server_default=match_seq.next_value())

    name = db.Column(db.String(100), nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    balls_per_over = db.Column(db.BigInteger, nullable=False)
    match_type = db.Column(db.String(10), nullable=False)
    team1 = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'), nullable=False)
    team2 = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'), nullable=False)
    toss_won_by_team = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'))
    toss_winner_choice = db.Column(db.String(50))
    league_event_id = db.Column(db.BigInteger, db.ForeignKey('cricket.league_events.league_event_id'))
    cricsheet_id = db.Column(db.String(20))
    event_stage = db.Column(db.String(50))
    end_date = db.Column(db.Date)
    event_group = db.Column(db.String(50))
    cricbuzz_match_id = db.Column(db.String(100))

    match_outcome = db.relationship('MatchOutcome', uselist=False)
    league_event_info = db.relationship('LeagueEvent', uselist=False)
    team1_info = db.relationship('Team', uselist=False, foreign_keys=[team1])
    team2_info = db.relationship('Team', uselist=False, foreign_keys=[team2])
    toss_won_by_team_info = db.relationship('Team', uselist=False, foreign_keys=[toss_won_by_team])

    innings_list = db.relationship('Innings', uselist=True)
    playing_11_list = db.relationship('Playing11', uselist=True)

    def to_dict(self):
        return {
            'matchId': self.match_id,
            'name': self.name,
            'venue': self.venue,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'ballsPerOver': self.balls_per_over,
            'matchType': self.match_type,
            'team1': self.team1_info.to_dict() if self.team1_info else None,
            'team2': self.team2_info.to_dict() if self.team2_info else None,
            'tossWonTeam': self.toss_won_by_team_info.to_dict() if self.toss_won_by_team_info else None,
            'tossWinnerChoice': self.toss_winner_choice,
            'leagueEvent': self.league_event_info.to_dict() if self.league_event_info else None,
            #'cricsheet_id': self.cricsheet_id,
            'eventStage': self.event_stage,
            'endDate': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'eventGroup': self.event_group,
            #'cricbuzz_match_id': self.cricbuzz_match_id,
            'matchOutcome': self.match_outcome.to_dict() if self.match_outcome else None,
            'inningsList':[i.to_dict() for i in self.innings_list] if self.innings_list else None,
            'playing11List':[p11.to_dict() for p11 in self.playing_11_list] if self.playing_11_list else None

        }

    def to_dict_basic(self):
        return {
            'matchId': self.match_id,
            'name': self.name,
            'venue': self.venue,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'ballsPerOver': self.balls_per_over,
            'matchType': self.match_type,
            'team1': self.team1,
            'team2': self.team2,
            #'tossWonTeam': self.toss_won_by_team_info.to_dict() if self.toss_won_by_team_info else None,
            #'tossWinnerChoice': self.toss_winner_choice,
            'leagueEvent': self.league_event_info.to_dict() if self.league_event_info else None,
            #'cricsheet_id': self.cricsheet_id,
            'eventStage': self.event_stage,
            'endDate': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'eventGroup': self.event_group,
            #'cricbuzz_match_id': self.cricbuzz_match_id,
            'matchOutcome': self.match_outcome.to_dict() if self.match_outcome else None,
            #'inningsList':[i.to_dict() for i in self.innings_list] if self.innings_list else None,
            #'playing11List':[p11.to_dict() for p11 in self.playing_11_list] if self.playing_11_list else None

        }

    def __repr__(self):
        return f"Match(match_id={self.match_id}, name={self.name}, venue={self.venue}, date={self.date})"


class Innings(db.Model):
    __tablename__ = 'innings'
    __table_args__ = {'schema': 'cricket'}

    innings_seq = Sequence('CRIC_INNINGS_S', metadata=db.metadata)
    innings_id = db.Column(db.BigInteger, primary_key=True, server_default=innings_seq.next_value())

    match_id = db.Column(db.BigInteger, db.ForeignKey('cricket.matches.match_id'), nullable=False)
    team = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'), nullable=False)
    target_overs = db.Column(db.String(10))
    target_runs = db.Column(db.BigInteger)
    innings_number = db.Column(db.BigInteger)

    # Define relationships
    #match = db.relationship('Match', uselist=False)
    team_info = db.relationship('Team', uselist=False)
    powerplays_list = db.relationship('MatchPowerplay', uselist=True)

    def to_dict(self):
        return {
            'inningsId': self.innings_id,
            'matchId': self.match_id,
            'team': self.team_info.to_dict() if self.team_info else None,
            'targetOvers': self.target_overs,
            'targetRuns': self.target_runs,
            'number': self.innings_number,
            'powerplaysList': [p.to_dict() for p in self.powerplays_list] if self.powerplays_list else None

        }

    def __repr__(self):
        return f"Innings(innings_id={self.innings_id}, match_id={self.match_id}, team={self.team}, innings_number={self.innings_number})"


class Playing11(db.Model):
    __tablename__ = 'playing11'
    __table_args__ = {'schema': 'cricket'}

    playing11_seq = Sequence('CRIC_PLAYING11_S', metadata=db.metadata)
    playing11_id = db.Column(db.BigInteger, primary_key=True, server_default=playing11_seq.next_value())
    
    
    player1 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player2 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player3 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player4 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player5 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player6 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player7 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player8 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player9 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player10 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player11 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    keeper = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    subs_in_player = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    subs_out_player = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    subs_reason = db.Column(db.String(100))
    captain = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))

    team = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'),nullable=False)
    team_info = db.relationship('Team', uselist=False)

    match_id = db.Column(db.Integer, db.ForeignKey('cricket.matches.match_id', ondelete='CASCADE'), nullable=False)
    #match = db.relationship('Match', backref=db.backref('cricket.playing11', lazy='dynamic' ))

    #player_info relationships
    player1_info = db.relationship('Player', uselist=False, foreign_keys=[player1])
    player2_info = db.relationship('Player', uselist=False, foreign_keys=[player2])
    player3_info = db.relationship('Player', uselist=False, foreign_keys=[player3])
    player4_info = db.relationship('Player', uselist=False, foreign_keys=[player4])
    player5_info = db.relationship('Player', uselist=False, foreign_keys=[player5])
    player6_info = db.relationship('Player', uselist=False, foreign_keys=[player6])
    player7_info = db.relationship('Player', uselist=False, foreign_keys=[player7])
    player8_info = db.relationship('Player', uselist=False, foreign_keys=[player8])
    player9_info = db.relationship('Player', uselist=False, foreign_keys=[player9])
    player10_info = db.relationship('Player', uselist=False, foreign_keys=[player10])
    player11_info = db.relationship('Player', uselist=False, foreign_keys=[player11])
    keeper_info = db.relationship('Player', uselist=False, foreign_keys=[keeper])
    captain_info = db.relationship('Player', uselist=False, foreign_keys=[captain])
    subs_in_player_info = db.relationship('Player', uselist=False, foreign_keys=[subs_in_player])
    subs_out_player_info = db.relationship('Player', uselist=False, foreign_keys=[subs_out_player])
    


    def to_dict(self):
        return {
            'playing11Id': self.playing11_id,
            'player1': self.player1_info.to_dict() if self.player1_info else None,
            'player2': self.player2_info.to_dict() if self.player2_info else None,
            'player3': self.player3_info.to_dict() if self.player3_info else None,
            'player4': self.player4_info.to_dict() if self.player4_info else None,
            'player5': self.player5_info.to_dict() if self.player5_info else None,
            'player6': self.player6_info.to_dict() if self.player6_info else None,
            'player7': self.player7_info.to_dict() if self.player7_info else None,
            'player8': self.player8_info.to_dict() if self.player8_info else None,
            'player9': self.player9_info.to_dict() if self.player9_info else None,
            'player10': self.player10_info.to_dict() if self.player10_info else None,
            'player11': self.player11_info.to_dict() if self.player11_info else None,
            'keeper': self.keeper_info.to_dict() if self.keeper_info else None,
            'subsInPlayer': self.subs_in_player_info.to_dict() if self.subs_in_player_info else None,
            'subsOutPlayer': self.subs_out_player_info.to_dict() if self.subs_out_player_info else None,
            'subsReason': self.subs_reason,
            'captain': self.captain_info.to_dict() if self.captain_info else None,
            'team': self.team_info.to_dict() if self.team_info else None,
        }

    def __repr__(self):
        return f"<Playing11(playing11_id={self.playing11_id}, match_id={self.match_id}, team={self.team})>"


class MatchOutcome(db.Model):
    __tablename__ = 'match_outcomes'
    __table_args__ = {'schema': 'cricket'}

    match_outcome_seq = Sequence('CRIC_MATCH_OUTCOMES_S', metadata=db.metadata)
    match_outcome_id = db.Column(db.BigInteger, primary_key=True, server_default=match_outcome_seq.next_value())

    match_id = db.Column(db.Integer, db.ForeignKey('cricket.matches.match_id', ondelete='CASCADE'), nullable=False)
    outcome = db.Column(db.String(50))
    winner = db.Column(db.String(100), db.ForeignKey('cricket.teams.name'))
    man_of_the_match = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    method = db.Column(db.String(20))

    #match = db.relationship('Match', backref=db.backref('cricket.match_outcomes', lazy='dynamic' ))

    man_of_the_match_info =  db.relationship('Player', uselist=False, foreign_keys=[man_of_the_match])   
    winner_info = db.relationship('Team', uselist=False, foreign_keys=[winner])  

    def to_dict(self):
        return {
            'matchOutcomeId': self.match_outcome_id,
            'outcome': self.outcome,
            'winner': self.winner_info.to_dict() if self.winner_info else None,
            'manOfTheMatch': self.man_of_the_match_info.to_dict() if self.man_of_the_match_info else None,
            'method': self.method
        }

    def __repr__(self):
        return f"<MatchOutcome(match_outcome_id={self.match_outcome_id}, match_id={self.match_id}, " \
               f"outcome={self.outcome}, winner={self.winner}, man_of_the_match={self.man_of_the_match}, " \
               f"method={self.method})>"


class MatchPowerplay(db.Model):
    __tablename__ = 'match_powerplays'
    __table_args__ = {'schema': 'cricket'}

    match_powerplay_seq = Sequence('CRIC_MATCH_POWERPLAYS_S', metadata=db.metadata)
    match_powerplay_id = db.Column(db.BigInteger, primary_key=True, server_default=match_powerplay_seq.next_value())

    innings_id = db.Column(db.Integer, db.ForeignKey('cricket.innings.innings_id', ondelete='CASCADE'), nullable=False)
    powerplay_from = db.Column(db.String(10), nullable=False)
    powerplay_to = db.Column(db.String(10), nullable=False)
    powerplay_kind = db.Column(db.String(50), nullable=False)

    #innings = db.relationship('Innings')

    def to_dict(self):
        return {
            'powerplayId': self.match_powerplay_id,
            #'innings_id': self.innings_id,
            'from': self.powerplay_from,
            'to': self.powerplay_to,
            'kind': self.powerplay_kind
        }
    
    def __repr__(self):
        return f"<MatchPowerplay(match_powerplay_id={self.match_powerplay_id}, innings_id={self.innings_id}, " \
               f"powerplay_from={self.powerplay_from}, powerplay_to={self.powerplay_to}, " \
               f"powerplay_kind={self.powerplay_kind})>"


class Delivery(db.Model):
    __tablename__ = 'deliveries'
    __table_args__ = {'schema': 'cricket'}
    
    delivery_id_seq = Sequence('CRIC_DELIVERIES_S', metadata=db.metadata)
    delivery_id = db.Column(db.BigInteger, primary_key=True, server_default=delivery_id_seq.next_value())
    
    innings_id = db.Column(db.BigInteger, db.ForeignKey('cricket.innings.innings_id', ondelete='CASCADE'), nullable=False)
    
    over = db.Column(db.BigInteger, nullable=False)
    indicator = db.Column(db.String(10), nullable=False)
    cricinfo_commentary = db.Column(db.String)
    cricbuzz_commentary = db.Column(db.String)

    batter = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    non_striker = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    bowler = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))

    # Define relationships
    #innings = db.relationship('Innings', backref=db.backref('cricket.deliveries', lazy='dynamic' ))
    batter_info = db.relationship('Player', uselist=False, foreign_keys=[batter])
    non_striker_info = db.relationship('Player', uselist=False, foreign_keys=[non_striker])
    bowler_info = db.relationship('Player', uselist=False, foreign_keys=[bowler])

    # children
    runs = db.relationship('Runs', uselist=False)
    extras = db.relationship('Extras', uselist=False)
    wicket = db.relationship('Wicket', uselist=False)
    #replacement = db.relationship('Replacement', uselist=False)
    review = db.relationship('Review', uselist=False)

    def to_dict(self):
        return {
            'deliveryId': self.delivery_id,
            'over': self.over,
            'indicator': self.indicator,
            #'innings': self.innings,
            'batter': self.batter_info.to_dict() if self.batter_info else None,
            'nonStriker': self.non_striker_info.to_dict() if self.non_striker_info else None,
            'bowler': self.bowler_info.to_dict() if self.bowler_info else None,
            'cricinfoComm': self.cricinfo_commentary,
            'cricbuzzComm': self.cricbuzz_commentary,
            'runs': self.runs.to_dict() if self.runs else None,
            'extras': self.extras.to_dict() if self.extras else None,
            'wicket': self.wicket.to_dict() if self.wicket else None,
            'review': self.review.to_dict() if self.review else None,
            #'replacement': self.replacement.to_dict() if self.replacement else None,
        }


    @staticmethod
    def find_deliveries_by_innings(inn_id):
        return Delivery.query.filter_by(innings_id=inn_id).all()

    def __repr__(self):
        return f"Delivery(delivery_id={self.delivery_id}, innings_id={self.innings_id}, over={self.over}, indicator={self.indicator})"


class Runs(db.Model):
    __tablename__ = 'runs'
    __table_args__ = {'schema': 'cricket'}

    runs_seq = Sequence('CRIC_RUNS_S', metadata=db.metadata)
    runs_id = db.Column(db.BigInteger, primary_key=True, server_default=runs_seq.next_value())
    
    
    delivery_id = db.Column(db.Integer, db.ForeignKey('cricket.deliveries.delivery_id', ondelete='CASCADE'), nullable=False)
    batter_runs = db.Column(db.Integer, nullable=False, default=0)
    extra_runs = db.Column(db.Integer, nullable=False, default=0)
    total_runs = db.Column(db.Integer, nullable=False, default=0)

    #delivery = db.relationship('Delivery', viewonly=True)

    def to_dict(self):
        return {
            'runsId': self.runs_id,
            #'deliveryId': self.delivery_id,
            'batterRuns': self.batter_runs,
            'extraRuns': self.extra_runs,
            'totalRuns': self.total_runs
        }

    def __repr__(self):
        return f"<Runs(runs_id={self.runs_id}, delivery_id={self.delivery_id}, batter_runs={self.batter_runs}, " \
               f"extra_runs={self.extra_runs}, total_runs={self.total_runs})>"


class Wicket(db.Model):
    __tablename__ = 'wickets'
    __table_args__ = {'schema': 'cricket'}

    wicket_seq = Sequence('CRIC_WICKETS_S', metadata=db.metadata)
    wicket_id = db.Column(db.BigInteger, primary_key=True, server_default=wicket_seq.next_value())
    
    
    delivery_id = db.Column(db.Integer, db.ForeignKey('cricket.deliveries.delivery_id', ondelete='CASCADE'), nullable=False)
    player_out = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    kind = db.Column(db.String(50), nullable=False)
    fielder1 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    fielder2 = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    bowler = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))

    #delivery = db.relationship('Delivery', viewonly=True)

    player_out_info = db.relationship('Player', foreign_keys=[player_out])
    bowler_info = db.relationship('Player', foreign_keys=[bowler])
    fielder1_info = db.relationship('Player', foreign_keys=[fielder1])
    fielder2_info = db.relationship('Player', foreign_keys=[fielder2])

    def to_dict(self):
        wicket_dict = {
            'wicketId': self.wicket_id,
            #'deliveryId': self.delivery_id,
            'kind': self.kind,
            'playerOut': self.player_out_info.to_dict() if self.player_out_info else None,
            'bowler': self.bowler_info.to_dict() if self.bowler_info else None,
            'fielder1': self.fielder1_info.to_dict() if self.fielder1_info else None,
            'fielder2': self.fielder2_info.to_dict() if self.fielder2_info else None
        }
        return wicket_dict

    def __repr__(self):
        return f"<Wicket(wicket_id={self.wicket_id}, kind={self.kind})>"


class Extras(db.Model):
    __tablename__ = 'extras'
    __table_args__ = {'schema': 'cricket'}

    extras_seq = Sequence('CRIC_EXTRAS_S', metadata=db.metadata)
    extras_id = db.Column(db.BigInteger, primary_key=True, server_default=extras_seq.next_value())
    
    
    delivery_id = db.Column(db.Integer, db.ForeignKey('cricket.deliveries.delivery_id', ondelete='CASCADE'), nullable=False)
    byes = db.Column(db.Integer, nullable=False, default=0)
    legbyes = db.Column(db.Integer, nullable=False, default=0)
    wides = db.Column(db.Integer, nullable=False, default=0)
    noballs = db.Column(db.Integer, nullable=False, default=0)
    others = db.Column(db.Integer, nullable=False, default=0)

    #delivery = db.relationship('Delivery', viewonly=True)

    def to_dict(self):
        extras_dict = {
            'extrasid': self.extras_id,
            #'delivery_id': self.delivery_id,
            'byes': self.byes,
            'legbyes': self.legbyes,
            'wides': self.wides,
            'noballs': self.noballs,
            'others': self.others
        }
        return extras_dict

    def __repr__(self):
        return f"<Extras(extras_id={self.extras_id}, byes={self.byes}, legbyes={self.legbyes}, wides={self.wides}, noballs={self.noballs}, others={self.others})>"


class Review(db.Model):
    __tablename__ = 'reviews'
    __table_args__ = {'schema': 'cricket'}

    review_seq = Sequence('CRIC_REVIEWS_S', metadata=db.metadata)
    review_id = db.Column(db.BigInteger, primary_key=True, server_default=review_seq.next_value())
    
    delivery_id = db.Column(db.Integer, db.ForeignKey('cricket.deliveries.delivery_id', ondelete='CASCADE'), nullable=False)
    taken_by = db.Column(db.String(200), nullable=False)
    batter = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'), nullable=False)
    umpire = db.Column(db.String(200), nullable=True)
    decision = db.Column(db.String(200), nullable=True)
    review_type = db.Column(db.String(50), nullable=True)
    umpires_call = db.Column(db.Integer, nullable=True)

    # Relationships
    #delivery = db.relationship('Delivery', viewonly=True)
    batter_info = db.relationship('Player', foreign_keys=[batter])

    def to_dict(self):
        review_dict = {
            'reviewId': self.review_id,
            #'delivery_id': self.delivery_id,
            'takenBy': self.taken_by,
            'batter': self.batter_info.to_dict() if self.batter_info else None,  # Include batter details
            'umpire': self.umpire,
            'decision': self.decision,
            'type': self.review_type,
            'umpiresCall': self.umpires_call
        }
        return review_dict

    def __repr__(self):
        return f"<Review(review_id={self.review_id}, delivery_id={self.delivery_id}, taken_by={self.taken_by}, batter_id={self.batter}, umpire={self.umpire}, decision={self.decision}, review_type={self.review_type}, umpires_call={self.umpires_call})>"


class Replacement(db.Model):
    __tablename__ = 'replacements'
    __table_args__ = {'schema': 'cricket'}

    replacement_seq = Sequence('CRIC_REPLACEMENTS_S', metadata=db.metadata)
    replacement_id = db.Column(db.BigInteger, primary_key=True, server_default=replacement_seq.next_value())
    
    delivery_id =  db.Column(db.Integer, db.ForeignKey('cricket.deliveries.delivery_id', ondelete='CASCADE'), nullable=False)
    kind = db.Column(db.String(10), nullable=True)
    player_in = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player_out = db.Column(db.Integer, db.ForeignKey('cricket.players.player_id'))
    player_role = db.Column(db.String(50), nullable=True)
    reason = db.Column(db.String(200), nullable=True)
    team = db.Column(db.String(200), db.ForeignKey('cricket.teams.name'), nullable=False)

    #delivery = db.relationship('Delivery', viewonly=True)
    player_in_info = db.relationship('Player', foreign_keys=[player_in])
    player_out_info = db.relationship('Player', foreign_keys=[player_out])
    team_info = db.relationship('Team', foreign_keys=[team])

    def to_dict(self):
        replacement_dict = {
            'replacementId': self.replacement_id,
            #'deliveryId': self.delivery_id,
            'kind': self.kind,
            'playerIn': self.player_in_info.to_dict() if self.player_in_info else None,
            'playerOut': self.player_out_info.to_dict() if self.player_out_info else None,
            'playerRole': self.player_role,
            'reason': self.reason,
            'team': self.team_info.to_dict() if self.team_info else None
        }
        return replacement_dict

    def __repr__(self):
        return f"<Replacement(replacement_id={self.replacement_id}, kind={self.kind}, player_in_id={self.player_in}, player_out_id={self.player_out}, player_role={self.player_role}, reason={self.reason}, team_name={self.team})>"


class Umpire(db.Model):
    __tablename__ = 'umpires'
    __table_args__ = {'schema': 'cricket'}

    umpire_seq = Sequence('CRIC_UMPIRES_S', metadata=db.metadata)
    umpire_id = db.Column(db.BigInteger, primary_key=True, server_default=umpire_seq.next_value())
    
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=True)
    cricsheet_id = db.Column(db.String(50), nullable=True, unique=True)
    cricinfo_id = db.Column(db.String(50), nullable=True, unique=True)
    cricsheet_name = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        umpire_dict = {
            'umpireId': self.umpire_id,
            'name': self.name,
            'country': self.country,
            'cricsheetId': self.cricsheet_id,
            'cricinfoId': self.cricinfo_id,
            'cricsheetName': self.cricsheet_name
        }
        return umpire_dict

    def __repr__(self):
        return f"<Umpire(umpire_id={self.umpire_id}, name={self.name}, country={self.country}, cricsheet_id={self.cricsheet_id}, cricinfo_id={self.cricinfo_id}, cricsheet_name={self.cricsheet_name})>"


class Lookup(db.Model):
    __tablename__ = 'lookups'
    __table_args__ = {'schema': 'cricket'}

    lookup_seq = Sequence('CRIC_LOOKUPS_S', metadata=db.metadata)
    lookup_id = db.Column(db.BigInteger, primary_key=True, server_default=lookup_seq.next_value())
    
    group = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    meaning = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    comments = db.Column(db.String, nullable=True)

    def to_dict(self):
        lookup_dict = {
            'lookupId': self.lookup_id,
            'group': self.group,
            'code': self.code,
            'meaning': self.meaning,
            'description': self.description,
            'comments': self.comments
        }
        return lookup_dict

    def __repr__(self):
        return f"<Lookup(lookup_id={self.lookup_id}, group={self.group}, code={self.code}, meaning={self.meaning}, description={self.description}, comments={self.comments})>"

