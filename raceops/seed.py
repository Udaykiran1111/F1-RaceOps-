from datetime import datetime, timezone, timedelta
import random, uuid
from .validation import install_validators
from .db import ensure_indexes

TEAMS = ["McLaren","Ferrari","Mercedes","Red Bull Racing","Aston Martin","Alpine","Williams","RB","Haas","Kick Sauber"]
DRIVERS = [
 ("D01","Lando Norris","McLaren",4),("D02","Oscar Piastri","McLaren",81),
 ("D03","Charles Leclerc","Ferrari",16),("D04","Lewis Hamilton","Ferrari",44),
 ("D05","George Russell","Mercedes",63),("D06","Andrea Kimi Antonelli","Mercedes",12),
 ("D07","Max Verstappen","Red Bull Racing",1),("D08","Liam Lawson","Red Bull Racing",30),
 ("D09","Fernando Alonso","Aston Martin",14),("D10","Lance Stroll","Aston Martin",18),
 ("D11","Pierre Gasly","Alpine",10),("D12","Franco Colapinto","Alpine",43),
 ("D13","Alex Albon","Williams",23),("D14","Carlos Sainz","Williams",55),
 ("D15","Yuki Tsunoda","RB",22),("D16","Isack Hadjar","RB",6),
 ("D17","Esteban Ocon","Haas",31),("D18","Oliver Bearman","Haas",87),
 ("D19","Nico Hulkenberg","Kick Sauber",27),("D20","Gabriel Bortoleto","Kick Sauber",5)
]
COMPOUNDS = ["SOFT","MEDIUM","HARD"]

def seed_database(db, reset=False, historical_events=1200, seed=494):
    random.seed(seed)
    install_validators(db)
    ensure_indexes(db)
    if reset:
        for n in ["races","drivers","telemetry","pit_stops","incidents","strategy_decisions"]:
            db[n].delete_many({})
    if db.drivers.count_documents({}) == 0:
        db.drivers.insert_many([{"driver_id":i,"name":n,"team":t,"car_number":num,"active":True} for i,n,t,num in DRIVERS])
    if db.races.count_documents({"race_id":"RACE-DEMO"}) == 0:
        db.races.insert_one({"race_id":"RACE-DEMO","season":2026,"circuit":"Silverstone International Circuit (simulated)","total_laps":52,
          "status":"RUNNING","weather":"DRY","track_temp_c":34.0,"dataset_type":"SYNTHETIC_SIMULATION",
          "created_at":datetime.now(timezone.utc)})
    if db.telemetry.count_documents({"race_id":"RACE-DEMO"}) < historical_events:
        base_time = datetime.now(timezone.utc) - timedelta(minutes=historical_events)
        docs=[]
        for i in range(historical_events):
            driver=DRIVERS[i % len(DRIVERS)]
            lap=(i // len(DRIVERS)) % 52 + 1
            tyre_age=max(0, lap - random.choice([1,5,12,18]))
            compound=random.choice(COMPOUNDS)
            degradation=max(0,tyre_age)*random.uniform(0.025,0.085)
            lap_time=88.0 + random.uniform(-2.5,2.5) + degradation + (3 if compound=="HARD" else 0 if compound=="MEDIUM" else -1)
            docs.append({"event_id":str(uuid.uuid4()),"race_id":"RACE-DEMO","driver_id":driver[0],
              "timestamp":base_time+timedelta(seconds=i),"lap":lap,"sector":(i%3)+1,
              "speed_kmh":round(random.uniform(180,330),2),"throttle_pct":round(random.uniform(20,100),1),
              "brake_pct":round(random.uniform(0,80),1),"tyre_temp_c":round(random.uniform(75,112),1),
              "tyre_compound":compound,"tyre_age":tyre_age,"fuel_estimate_kg":round(max(1,100-lap*1.7),2),
              "lap_time_seconds":round(lap_time,3),"position":(i//len(DRIVERS))%20+1,
              "weather":"DRY","track_temp_c":34.0,"data_origin":"SYNTHETIC"})
        db.telemetry.insert_many(docs, ordered=False)
    if db.pit_stops.count_documents({"race_id":"RACE-DEMO"}) == 0:
        db.pit_stops.insert_many([
          {"race_id":"RACE-DEMO","driver_id":"D01","lap":18,"duration_seconds":2.42,"old_compound":"MEDIUM","new_compound":"HARD","position_before":3,"position_after":4,"data_origin":"SYNTHETIC"},
          {"race_id":"RACE-DEMO","driver_id":"D03","lap":21,"duration_seconds":2.71,"old_compound":"SOFT","new_compound":"MEDIUM","position_before":5,"position_after":5,"data_origin":"SYNTHETIC"},
          {"race_id":"RACE-DEMO","driver_id":"D07","lap":25,"duration_seconds":2.31,"old_compound":"MEDIUM","new_compound":"HARD","position_before":1,"position_after":2,"data_origin":"SYNTHETIC"}])
    if db.incidents.count_documents({"race_id":"RACE-DEMO"}) == 0:
        db.incidents.insert_many([
          {"race_id":"RACE-DEMO","lap":12,"type":"VIRTUAL_SAFETY_CAR","severity":"MEDIUM","description":"Simulated debris response","data_origin":"SYNTHETIC"},
          {"race_id":"RACE-DEMO","lap":31,"type":"RAIN","severity":"HIGH","description":"Simulated light rain cell","data_origin":"SYNTHETIC"}])
    return {"drivers":db.drivers.count_documents({}),"races":db.races.count_documents({}),
      "telemetry":db.telemetry.count_documents({"race_id":"RACE-DEMO"}),
      "pit_stops":db.pit_stops.count_documents({"race_id":"RACE-DEMO"}),
      "incidents":db.incidents.count_documents({"race_id":"RACE-DEMO"})}
