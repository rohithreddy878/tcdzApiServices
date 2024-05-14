# RESTAURANT_LIST = "restaurantsList"
# MENU_LIST = "menusList"
# FOOD_LIST = "foodsList"

BOWLER_CREDITED_WICKET_KINDS = ["lbw","caught","bowled","stumped","caught and bowled","hit wicket"];

ALL_WICKET_KINDS = ["caught","bowled","lbw","run out","stumped","caught and bowled","retired out","retired hurt","hit wicket","obstructing the field"];

FAVOURITE_BATSMEN_LIST = ["Virat Kohli","Steve Smith","Joe Root","Kane Williamson","Babar Azam"];
FAVOURITE_BOWLERS_LIST = ["Mitchell Starc","Ravichandran Ashwin","Jimmy Anderson","Pat Cummins","Kagiso Rabada"];
FAVOURITE_ALLROUNDERS_LIST = ["Ben Stokes","Ravindra Jadeja","Hardik Pandya","Cameron Green","Dasun Shanaka"];

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
    