from datetime import datetime, timezone

def recommend_strategy(latest, recent_laps=None, active_incident=None):
    # Transparent rule-based baseline, not a trained F1 team model.
    age = int(latest.get("tyre_age", 0))
    compound = latest.get("tyre_compound", "MEDIUM")
    temp = float(latest.get("tyre_temp_c", 90))
    action = "STAY_OUT"
    reasons=[]
    if active_incident in ("SAFETY_CAR","VIRTUAL_SAFETY_CAR"):
        action="PIT_NOW"; reasons.append("safety-car window may reduce pit-loss")
    elif age >= (SOFT_LIMIT if compound=="SOFT" else MEDIUM_LIMIT if compound=="MEDIUM" else HARD_LIMIT):
        action="PIT_SOON"; reasons.append("tyre-age threshold reached")
    elif temp >= 108:
        action="MONITOR"; reasons.append("tyre temperature is high")
    else:
        reasons.append("tyre age and temperature remain within configured thresholds")
    confidence = 0.72 if action in ("PIT_NOW","PIT_SOON") else 0.62
    return {"recommended_action":action,"recommended_compound":"HARD" if compound!="HARD" else "MEDIUM",
      "confidence":confidence,"risk":"HIGH" if action=="PIT_NOW" else "MEDIUM" if action in ("PIT_SOON","MONITOR") else "LOW",
      "reasons":reasons,"model_type":"RULE_BASED_DEMO","timestamp":datetime.now(timezone.utc)}

SOFT_LIMIT=14
MEDIUM_LIMIT=22
HARD_LIMIT=30

def save_decision(db, race_id, driver_id, latest, incident=None):
    result=recommend_strategy(latest, active_incident=incident)
    result.update({"race_id":race_id,"driver_id":driver_id,"lap":latest.get("lap"),"data_origin":"SIMULATED"})
    db.strategy_decisions.insert_one(result)
    return result
