from raceops.db import get_client, get_db
# Change Streams require a replica set (MongoDB Atlas supports this).
client=get_client()
try:
 db=get_db(client)
 print("Watching telemetry inserts. Press Ctrl+C to stop.")
 with db.telemetry.watch([{"$match":{"operationType":"insert"}}], full_document="default") as stream:
  for change in stream:
   doc=change["fullDocument"]
   print("NEW EVENT:",doc.get("driver_id"),"lap",doc.get("lap"),"speed",doc.get("speed_kmh"))
except Exception as e:
 print("Change Stream unavailable. This usually means standalone MongoDB is being used.")
 print("Core simulator and polling dashboard can still work. Details:",repr(e))
finally:
 client.close()
