def driver_pace_summary(db, race_id="RACE-DEMO"):
    pipeline=[
      {"$match":{"race_id":race_id}},
      {"$group":{"_id":"$driver_id","events":{"$sum":1},"avg_lap_time":{"$avg":"$lap_time_seconds"},
        "avg_speed":{"$avg":"$speed_kmh"},"max_tyre_age":{"$max":"$tyre_age"},
        "avg_tyre_temp":{"$avg":"$tyre_temp_c"}}},
      {"$sort":{"avg_lap_time":1}}
    ]
    return list(db.telemetry.aggregate(pipeline))

def compound_performance(db, race_id="RACE-DEMO"):
    pipeline=[
      {"$match":{"race_id":race_id}},
      {"$group":{"_id":"$tyre_compound","events":{"$sum":1},"avg_lap_time":{"$avg":"$lap_time_seconds"},
        "avg_tyre_age":{"$avg":"$tyre_age"},"avg_temp":{"$avg":"$tyre_temp_c"}}},
      {"$sort":{"avg_lap_time":1}}
    ]
    return list(db.telemetry.aggregate(pipeline))

def pit_loss_by_team(db, race_id="RACE-DEMO"):
    pipeline=[
      {"$match":{"race_id":race_id}},
      {"$lookup":{"from":"drivers","localField":"driver_id","foreignField":"driver_id","as":"driver"}},
      {"$unwind":{"path":"$driver","preserveNullAndEmptyArrays":True}},
      {"$addFields":{"position_delta":{"$subtract":["$position_after","$position_before"]}}},
      {"$group":{"_id":"$driver.team","stops":{"$sum":1},"avg_stop_seconds":{"$avg":"$duration_seconds"},
        "avg_position_delta":{"$avg":"$position_delta"}}},
      {"$sort":{"avg_stop_seconds":1}}
    ]
    return list(db.pit_stops.aggregate(pipeline))

def incident_summary(db, race_id="RACE-DEMO"):
    return list(db.incidents.aggregate([
      {"$match":{"race_id":race_id}},
      {"$group":{"_id":{"type":"$type","severity":"$severity"},"count":{"$sum":1}}},
      {"$sort":{"count":-1}}
    ]))

def strategy_action_counts(db, race_id="RACE-DEMO"):
    return list(db.strategy_decisions.aggregate([
      {"$match":{"race_id":race_id}},
      {"$group":{"_id":"$recommended_action","count":{"$sum":1}}},
      {"$sort":{"count":-1}}
    ]))
