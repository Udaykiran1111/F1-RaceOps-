from datetime import datetime, timezone
from bson import ObjectId

def create_driver(db, driver_id, name, team, car_number):
    doc={"driver_id":driver_id,"name":name,"team":team,"car_number":int(car_number),"active":True}
    return db.drivers.insert_one(doc).inserted_id

def read_driver(db, driver_id):
    return db.drivers.find_one({"driver_id":driver_id}, {"_id":0})

def update_driver_team(db, driver_id, team):
    return db.drivers.update_one({"driver_id":driver_id},{"$set":{"team":team}}).modified_count

def delete_driver(db, driver_id):
    return db.drivers.delete_one({"driver_id":driver_id}).deleted_count

def latest_telemetry(db, race_id="RACE-DEMO", limit=20):
    return list(db.telemetry.find({"race_id":race_id},{"_id":0}).sort("timestamp",-1).limit(limit))
