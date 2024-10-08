BOWLER_CREDITED_WICKET_KINDS = ["lbw","caught","bowled","stumped","caught and bowled","hit wicket"];

ALL_WICKET_KINDS = ["caught","bowled","lbw","run out","stumped","caught and bowled","retired out","retired hurt","hit wicket","obstructing the field"];

FAVOURITE_BATSMEN_LIST = ["Virat Kohli","Kieron Pollard"];
FAVOURITE_BOWLERS_LIST = ["Ravichandran Ashwin","Jasprit Bumrah","Sunil Narine"];
FAVOURITE_ALLROUNDERS_LIST = ["Ravindra Jadeja","Hardik Pandya","Andre Russell"];

BATTING_HIGHLIGHTS_REMOVABLE_WORDS= ['delivery', 'bat','ball', 'boundary', 'fielder', 'runs', 'fence', 'man','four','six','maximum']

PLAYERS_SEARCH_QUERY = """
SELECT *
FROM cricket.players pl
WHERE (UPPER(pl.name) LIKE :searchNameParam OR UPPER(pl.common_name) LIKE :searchNameParam)
AND pl.player_id IN (
    SELECT DISTINCT player1 AS player FROM cricket.Playing11 
    UNION SELECT DISTINCT player2 AS player FROM cricket.Playing11
    UNION SELECT DISTINCT player3 AS player FROM cricket.Playing11 
    UNION SELECT DISTINCT player4 AS player FROM cricket.Playing11
    UNION SELECT DISTINCT player5 AS player FROM cricket.Playing11 
    UNION SELECT DISTINCT player6 AS player FROM cricket.Playing11
    UNION SELECT DISTINCT player7 AS player FROM cricket.Playing11 
    UNION SELECT DISTINCT player8 AS player FROM cricket.Playing11
    UNION SELECT DISTINCT player9 AS player FROM cricket.Playing11 
    UNION SELECT DISTINCT player10 AS player FROM cricket.Playing11
    UNION SELECT DISTINCT player11 AS player FROM cricket.Playing11 
    UNION SELECT DISTINCT subs_in_player AS player FROM cricket.Playing11
);
"""

DELIVERIES_FOR_INNINGS_FETCH_QUERY = """
    SELECT d.delivery_id,d.batter, d.bowler, 
        r.runs_id, r.batter_runs,r.extra_runs,r.total_runs,
        w.wicket_id,w.player_out,w.kind,w.fielder1,w.fielder2,
        e.extras_id,e.wides,e.noballs
    FROM cricket.deliveries d
    JOIN cricket.runs r ON d.delivery_id = r.delivery_id
    LEFT JOIN cricket.wickets w ON d.delivery_id = w.delivery_id
    LEFT JOIN cricket.extras e ON d.delivery_id = e.delivery_id
    WHERE d.innings_id = :inningsIdParam
    ORDER BY d.innings_id, d.over asc, d.indicator asc;
"""

# player career stats query

PLAYER_TOTAL_IPL_MATCHES_PLAYED = """
	SELECT count(*) FROM cricket.Playing11 p
	WHERE p.match_id in (SELECT m.match_id FROM cricket.matches m WHERE m.league_event_id in (SELECT l.league_event_id FROM cricket.league_events l WHERE l.league_id=6))
    	AND (p.player1 = :playerIdParam OR p.player2 = :playerIdParam OR p.player3 = :playerIdParam OR
    	p.player4 = :playerIdParam OR p.player5 = :playerIdParam OR p.player6 = :playerIdParam OR
    	p.player7 = :playerIdParam OR p.player8 = :playerIdParam OR p.player9 = :playerIdParam OR
    	p.player10 = :playerIdParam OR p.player11 = :playerIdParam OR p.subs_in_player = :playerIdParam);
"""

PLAYER_INNINGS_BATTED_QUERY="SELECT DISTINCT d.innings_id FROM cricket.Deliveries d WHERE d.batter = :playerIdParam;"
PLAYER_INNINGS_BOWLED_QUERY="SELECT DISTINCT d.innings_id FROM cricket.Deliveries d WHERE d.bowler = :playerIdParam;"


BATTER_RUNS_SCORED_QUERY="SELECT sum(r.batter_runs) FROM cricket.Runs r where r.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.batter = :playerIdParam);"
BATTER_BALLS_FACED_QUERY="SELECT COUNT(*) FROM cricket.Deliveries d LEFT JOIN cricket.Extras e ON d.delivery_id = e.delivery_id WHERE d.batter = :playerIdParam AND (e.wides IS NULL OR e.wides = 0);"
BATTER_FOURS_SCORED_QUERY="SELECT count(*) FROM cricket.Runs r where r.batter_runs=4 AND r.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.batter = :playerIdParam);"
BATTER_SIXES_SCORED_QUERY="SELECT count(*) FROM cricket.Runs r where r.batter_runs=6 AND r.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.batter = :playerIdParam);"
BATTER_NUMBER_OF_OUTS_QUERY="SELECT count(*) FROM cricket.Wickets w where w.player_out=:playerIdParam AND w.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.batter = :playerIdParam);"
BATTER_HIGHEST_SCORE_QUERY="""
	SELECT MAX(innings_runs) FROM (
    	SELECT SUM(r.batter_runs) AS innings_runs
    	FROM cricket.Deliveries d LEFT JOIN cricket.Runs r ON d.delivery_id = r.delivery_id
    	WHERE d.batter = :playerIdParam GROUP BY d.innings_id);
""" 
BATTER_LANDMARK_SCORES_QUERY="""
	SELECT COUNT(*)
	FROM (
    	SELECT SUM(r.batter_runs) AS innings_runs
    	FROM cricket.Deliveries d LEFT JOIN cricket.Runs r ON d.delivery_id = r.delivery_id
    	WHERE d.batter=:playerIdParam GROUP BY d.innings_id) 
	WHERE innings_runs >= :landmarkParam;
"""

BOWLER_BALLS_BOWLED_QUERY="SELECT COUNT(*) FROM cricket.Deliveries d LEFT JOIN cricket.Extras e ON d.delivery_id = e.delivery_id WHERE d.bowler=:playerIdParam AND (e.extras_id IS NULL OR (e.wides=0 AND e.noballs=0));"
BOWLER_ALL_RUNS_CONCEDED_QUERY="SELECT sum(r.total_runs) FROM cricket.Runs r where r.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.bowler=:playerIdParam);"
BOWLER_BYES_CONCEDED_QUERY="SELECT sum(e.byes)+sum(legbyes) AS byes FROM cricket.extras e where e.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.bowler=:playerIdParam);"

BOWLER_WICKETS_TAKEN_QUERY="""
	SELECT count(*) FROM cricket.Wickets w 
	WHERE w.delivery_id in (SELECT d.delivery_id FROM cricket.Deliveries d WHERE d.bowler=:playerIdParam)
	AND w.kind in ('lbw','caught','bowled','stumped','caught and bowled','hit wicket');
"""
BOWLER_LANDMARK_WICKETS_QUERY="""
	SELECT COUNT(*)
	FROM (
    	SELECT count(*) AS wicketsTakenInMatch
    	FROM cricket.Deliveries d LEFT JOIN  cricket.Wickets w  ON d.delivery_id = w.delivery_id
    	WHERE d.bowler=:playerIdParam AND w.kind in ('lbw','caught','bowled','stumped','caught and bowled','hit wicket')
        GROUP BY d.innings_id) 
	WHERE wicketsTakenInMatch >= :landmarkParam;
"""

PLAYER_PLAYED_TEAMS_QUERY = """
	WITH RankedTeams AS (
    	SELECT p.team AS played_team, m."date", ROW_NUMBER() OVER (PARTITION BY p.team ORDER BY m."date" DESC) AS rn
    	FROM cricket.matches m LEFT JOIN cricket.Playing11 p ON p.match_id = m.match_id
    	WHERE m.league_event_id IN (SELECT l.league_event_id FROM cricket.league_events l WHERE l.league_id = 6)
    	AND (p.player1 = :playerIdParam OR p.player2 = :playerIdParam OR p.player3 = :playerIdParam OR
        	p.player4 = :playerIdParam OR p.player5 = :playerIdParam OR p.player6 = :playerIdParam OR
        	p.player7 = :playerIdParam OR p.player8 = :playerIdParam OR p.player9 = :playerIdParam OR
        	p.player10 = :playerIdParam OR p.player11 = :playerIdParam OR p.subs_in_player = :playerIdParam))
	SELECT played_team FROM RankedTeams WHERE rn = 1 ORDER BY "date" DESC;
"""

# Commentary Analysis queries

PLAYER_RUNS_SCORED_COMMS_QUERY = """
SELECT d.delivery_id,d.bowler,d.cricbuzz_commentary, 
(SELECT m.date FROM cricket.matches m 
    WHERE m.match_id=(SELECT i.match_id FROM cricket.innings i WHERE i.innings_id=d.innings_id)) as dat 
FROM cricket.deliveries d LEFT JOIN cricket.runs r ON r.delivery_id=d.delivery_id
WHERE d.innings_id in (SELECT innings_id FROM cricket.innings WHERE match_id in (SELECT match_id FROM cricket.matches WHERE league_event_id in (14,22,16,27,21,28,25)))
AND d.batter=:playerIdParam  AND r.batter_runs=:runsParam
ORDER BY dat desc;
"""

PLAYER_GOT_OUT_COMMS_QUERY = """
SELECT d.delivery_id,d.bowler,d.cricbuzz_commentary, w.kind,
(SELECT m.date FROM cricket.matches m 
    WHERE m.match_id=(SELECT i.match_id FROM cricket.innings i WHERE i.innings_id=d.innings_id)) as dat 
FROM cricket.deliveries d LEFT JOIN cricket.wickets w ON d.delivery_id=w.delivery_id
WHERE d.innings_id in (SELECT innings_id FROM cricket.innings WHERE match_id in (SELECT match_id FROM cricket.matches WHERE league_event_id in (14,22,16,27,21,28,25)))
AND w.player_out=:playerIdParam
ORDER BY dat desc;
"""










    