from raceops.db import get_client, get_db
from raceops.crud import create_driver, read_driver, update_driver_team, delete_driver
client=get_client()
try:
 db=get_db(client)
 test_id="DEMO-CRUD-01"
 db.drivers.delete_many({"driver_id":test_id})
 create_driver(db,test_id,"Demo Driver","Demo Team",99)
 print("CREATE + READ:",read_driver(db,test_id))
 print("UPDATE modified:",update_driver_team(db,test_id,"Updated Demo Team"))
 print("READ after update:",read_driver(db,test_id))
 print("DELETE count:",delete_driver(db,test_id))
 print("READ after delete:",read_driver(db,test_id))
finally: client.close()
