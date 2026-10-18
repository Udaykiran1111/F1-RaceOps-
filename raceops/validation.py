from datetime import datetime
from pymongo.errors import DuplicateKeyError

# MongoDB server-side validators are installed by setup_database().
VALIDATORS = {
 "drivers": {"$jsonSchema": {"bsonType":"object","required":["driver_id","name","team"],"properties":{
  "driver_id":{"bsonType":"string","minLength":1},"name":{"bsonType":"string","minLength":1},
  "team":{"bsonType":"string","minLength":1},"car_number":{"bsonType":["int","long"],"minimum":1,"maximum":99}}}},
 "races": {"$jsonSchema": {"bsonType":"object","required":["race_id","circuit","total_laps","status"],"properties":{
  "race_id":{"bsonType":"string"},"circuit":{"bsonType":"string"},
  "total_laps":{"bsonType":["int","long"],"minimum":1,"maximum":100},
  "status":{"enum":["SCHEDULED","RUNNING","COMPLETED","ABORTED"]}}}},
 "telemetry": {"$jsonSchema": {"bsonType":"object","required":["event_id","race_id","driver_id","timestamp","lap","speed_kmh","tyre_compound","tyre_age"],"properties":{
  "event_id":{"bsonType":"string"},"race_id":{"bsonType":"string"},"driver_id":{"bsonType":"string"},
  "timestamp":{"bsonType":"date"},"lap":{"bsonType":["int","long"],"minimum":1},
  "speed_kmh":{"bsonType":["double","int","long"],"minimum":0,"maximum":380},
  "tyre_compound":{"enum":["SOFT","MEDIUM","HARD","INTERMEDIATE","WET"]},
  "tyre_age":{"bsonType":["int","long"],"minimum":0}}}},
 "pit_stops": {"$jsonSchema": {"bsonType":"object","required":["race_id","driver_id","lap","duration_seconds","new_compound"],"properties":{
  "race_id":{"bsonType":"string"},"driver_id":{"bsonType":"string"},"lap":{"bsonType":["int","long"],"minimum":1},
  "duration_seconds":{"bsonType":["double","int","long"],"minimum":1,"maximum":60},
  "new_compound":{"enum":["SOFT","MEDIUM","HARD","INTERMEDIATE","WET"]}}}},
 "incidents": {"$jsonSchema": {"bsonType":"object","required":["race_id","lap","type","severity"],"properties":{
  "race_id":{"bsonType":"string"},"lap":{"bsonType":["int","long"],"minimum":1},
  "type":{"enum":["SAFETY_CAR","VIRTUAL_SAFETY_CAR","RAIN","CRASH","DEBRIS","MECHANICAL"]},
  "severity":{"enum":["LOW","MEDIUM","HIGH","CRITICAL"]}}}},
 "strategy_decisions": {"$jsonSchema": {"bsonType":"object","required":["race_id","driver_id","timestamp","recommended_action","confidence"],"properties":{
  "race_id":{"bsonType":"string"},"driver_id":{"bsonType":"string"},"timestamp":{"bsonType":"date"},
  "recommended_action":{"enum":["STAY_OUT","PIT_SOON","PIT_NOW","MONITOR"]},
  "confidence":{"bsonType":["double","int","long"],"minimum":0,"maximum":1}}}}
}

def install_validators(db):
    existing = set(db.list_collection_names())
    for name, validator in VALIDATORS.items():
        if name not in existing:
            db.create_collection(name, validator=validator, validationLevel="strict", validationAction="error")
        else:
            db.command({"collMod": name, "validator": validator, "validationLevel":"strict", "validationAction":"error"})
    for name in ["drivers","races","telemetry","pit_stops","incidents","strategy_decisions"]:
        if name not in db.list_collection_names():
            db.create_collection(name)
    return True
