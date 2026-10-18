import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError, PyMongoError

from raceops.db import get_client
from raceops.config import MONGODB_URI, MONGODB_DB
from raceops.aggregations import (
    driver_pace_summary, compound_performance, incident_summary,
    strategy_action_counts,
)
from raceops.crud import latest_telemetry, create_driver, read_driver, update_driver_team, delete_driver
from raceops.seed import seed_database, TEAMS
from raceops.simulator import generate_event
from raceops.validation import install_validators

st.set_page_config(page_title="F1 RaceOps", page_icon="🏁", layout="wide")
st.title("🏁 F1 RaceOps")
st.caption("Race Operations, Synthetic Telemetry & Strategy Analytics")
uri = st.sidebar.text_input(
    "MongoDB URI", value=None, type="password",
    help="Leave blank to use MONGODB_URI from .env.",
)

client = None
try:
    from pymongo import MongoClient
    client = MongoClient(uri or MONGODB_URI, serverSelectionTimeoutMS=3000)
    db = client[MONGODB_DB]
    db.command("ping")
    install_validators(db)

    if st.sidebar.button("Seed / repair demo data"):
        summary = seed_database(db)
        st.sidebar.success(f"Demo data ready: {summary}")

    races = list(db.races.find({}, {"_id": 0}).sort("created_at", -1))
    race_ids = [r["race_id"] for r in races]
    if not race_ids:
        race_id = ""
        st.warning("No races exist yet. Open Race Management and create a race, or seed demo data.")
    else:
        default_idx = race_ids.index("RACE-DEMO") if "RACE-DEMO" in race_ids else 0
        race_id = st.sidebar.selectbox("Select race", race_ids, index=default_idx, key="selected_race")
        selected_race = next((r for r in races if r["race_id"] == race_id), {})
        st.sidebar.caption(f"{selected_race.get('circuit', 'Circuit not set')} · {selected_race.get('status', 'UNKNOWN')}")

    tabs = st.tabs(["Race Dashboard", "Race Management", "Driver Management", "Simulator & Events"])

    # TAB 1: dashboard
    with tabs[0]:
        st.subheader("Race overview")
        if race_id:
            total = db.telemetry.count_documents({"race_id": race_id})
            driver_count = db.drivers.count_documents({})
            incident_count = db.incidents.count_documents({"race_id": race_id})
            decision_count = db.strategy_decisions.count_documents({"race_id": race_id})
            a, b, c, d = st.columns(4)
            a.metric("Telemetry events", f"{total:,}")
            b.metric("Drivers registered", driver_count)
            c.metric("Incidents", incident_count)
            d.metric("Strategy decisions", decision_count)

            left, right = st.columns(2)
            with left:
                st.subheader("Tyre compound performance")
                comp = compound_performance(db, race_id)
                if comp:
                    df = pd.DataFrame([
                        {"Compound": x["_id"], "Average lap time (s)": round(x["avg_lap_time"], 3), "Events": x["events"]}
                        for x in comp
                    ])
                    st.plotly_chart(px.bar(df, x="Compound", y="Average lap time (s)", color="Compound"), use_container_width=True)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No telemetry for this race yet. Use Simulator & Events to generate it.")
            with right:
                st.subheader("Driver pace ranking")
                pace = driver_pace_summary(db, race_id)
                if pace:
                    names = {x["driver_id"]: x["name"] for x in db.drivers.find({}, {"driver_id": 1, "name": 1})}
                    df = pd.DataFrame([
                        {"Driver": names.get(x["_id"], x["_id"]), "Average lap time (s)": round(x["avg_lap_time"], 3),
                         "Average speed (km/h)": round(x["avg_speed"], 1), "Max tyre age": x["max_tyre_age"]}
                        for x in pace
                    ])
                    st.dataframe(df, use_container_width=True)
                    st.plotly_chart(px.bar(df.sort_values("Average lap time (s)"), x="Driver", y="Average lap time (s)"), use_container_width=True)
                else:
                    st.info("No driver pace data for this race.")

            st.subheader("Latest telemetry events")
            latest = latest_telemetry(db, race_id, 30)
            if latest:
                frame = pd.DataFrame(latest)
                if "_id" in frame:
                    frame = frame.drop(columns=["_id"])
                st.dataframe(frame, use_container_width=True)
            else:
                st.info("No telemetry events recorded yet.")

            x, y = st.columns(2)
            with x:
                st.subheader("Incidents by type / severity")
                rows = incident_summary(db, race_id)
                if rows:
                    st.dataframe(pd.DataFrame([
                        {"Type": r["_id"]["type"], "Severity": r["_id"]["severity"], "Count": r["count"]}
                        for r in rows
                    ]), use_container_width=True)
                else:
                    st.info("No incidents recorded.")
            with y:
                st.subheader("Strategy action distribution")
                rows = strategy_action_counts(db, race_id)
                if rows:
                    st.plotly_chart(px.pie(pd.DataFrame([
                        {"Action": r["_id"], "Count": r["count"]} for r in rows
                    ]), names="Action", values="Count"), use_container_width=True)
                else:
                    st.info("No strategy decisions yet. Generate telemetry to create them.")
        st.info("All generated data is SYNTHETIC / SIMULATED. Strategy recommendations are transparent demo rules, not official F1 advice.")

    # TAB 2: race management
    with tabs[1]:
        st.subheader("Create a race")
        st.write("Race metadata is stored in the MongoDB `races` collection. Race ID must be unique.")
        with st.form("create_race_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_race_id = st.text_input("Race ID", placeholder="RACE-2026-02")
                circuit = st.text_input("Circuit", placeholder="Autodromo Nazionale Monza")
                location = st.text_input("Location", placeholder="Monza, Italy")
                season = st.number_input("Season", min_value=2020, max_value=2100, value=2026, step=1)
            with col2:
                total_laps = st.number_input("Planned laps", min_value=1, max_value=100, value=53, step=1)
                status = st.selectbox("Status", ["SCHEDULED", "RUNNING", "COMPLETED", "ABORTED"])
                weather = st.selectbox("Weather", ["DRY", "WET", "MIXED"])
                track_temp = st.number_input("Track temperature (°C)", min_value=0.0, max_value=80.0, value=30.0, step=1.0)
            submitted = st.form_submit_button("Create race", type="primary")
            if submitted:
                new_race_id = new_race_id.strip().upper()
                circuit = circuit.strip()
                if not new_race_id or not circuit:
                    st.error("Race ID and circuit are required.")
                elif db.races.find_one({"race_id": new_race_id}):
                    st.error("That Race ID already exists. Choose a unique ID.")
                else:
                    doc = {
                        "race_id": new_race_id, "circuit": circuit, "location": location.strip(),
                        "season": int(season), "total_laps": int(total_laps), "status": status,
                        "weather": weather, "track_temp_c": float(track_temp),
                        "dataset_type": "SYNTHETIC_SIMULATION", "created_at": datetime.now(timezone.utc),
                    }
                    try:
                        db.races.insert_one(doc)
                        st.success(f"Created race {new_race_id}. Select it from the sidebar to view it.")
                        st.rerun()
                    except DuplicateKeyError:
                        st.error("That Race ID already exists.")
                    except PyMongoError as exc:
                        st.error(f"MongoDB rejected the race: {exc}")

        st.divider()
        st.subheader("Existing races")
        if races:
            race_frame = pd.DataFrame(races)
            if "created_at" in race_frame:
                race_frame["created_at"] = race_frame["created_at"].astype(str)
            st.dataframe(race_frame, use_container_width=True)
        else:
            st.info("No race records yet.")

        if races:
            st.subheader("Update race status")
            race_to_update = st.selectbox("Race to update", race_ids, key="status_race_id")
            current = next((r for r in races if r["race_id"] == race_to_update), {})
            statuses = ["SCHEDULED", "RUNNING", "COMPLETED", "ABORTED"]
            current_status = current.get("status", "SCHEDULED")
            selected_status = st.selectbox("New status", statuses, index=statuses.index(current_status) if current_status in statuses else 0)
            if st.button("Save race status"):
                db.races.update_one({"race_id": race_to_update}, {"$set": {"status": selected_status}})
                st.success(f"{race_to_update} status updated to {selected_status}.")
                st.rerun()

    # TAB 3: driver management
    with tabs[2]:
        st.subheader("Register a driver")
        with st.form("create_driver_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                driver_id = st.text_input("Driver ID", placeholder="D21")
                driver_name = st.text_input("Driver name")
            with c2:
                team = st.selectbox("Team", TEAMS + ["Other"])
                car_number = st.number_input("Car number", min_value=1, max_value=99, value=21)
            if st.form_submit_button("Register driver", type="primary"):
                driver_id = driver_id.strip().upper()
                driver_name = driver_name.strip()
                if not driver_id or not driver_name:
                    st.error("Driver ID and name are required.")
                elif db.drivers.find_one({"driver_id": driver_id}):
                    st.error("That Driver ID already exists.")
                else:
                    try:
                        create_driver(db, driver_id, driver_name, team, int(car_number))
                        st.success(f"Registered {driver_name} ({driver_id}).")
                        st.rerun()
                    except DuplicateKeyError:
                        st.error("That Driver ID already exists.")
                    except PyMongoError as exc:
                        st.error(f"Could not register driver: {exc}")

        st.divider()
        st.subheader("Existing drivers")
        driver_rows = list(db.drivers.find({}, {"_id": 0}).sort("driver_id", 1))
        if driver_rows:
            st.dataframe(pd.DataFrame(driver_rows), use_container_width=True)
            ids = [d["driver_id"] for d in driver_rows]
            chosen_driver = st.selectbox("Select driver to manage", ids)
            chosen_doc = next(d for d in driver_rows if d["driver_id"] == chosen_driver)
            st.write(f"**{chosen_doc.get('name')}** · {chosen_doc.get('team')} · car #{chosen_doc.get('car_number', 'N/A')}")
            new_team = st.selectbox("Change team", TEAMS + ["Other"], index=(TEAMS + ["Other"]).index(chosen_doc["team"]) if chosen_doc.get("team") in TEAMS + ["Other"] else 0)
            if st.button("Update driver team"):
                update_driver_team(db, chosen_driver, new_team)
                st.success("Driver team updated.")
                st.rerun()
            confirm_delete = st.checkbox("I understand deleting a driver can leave historical records referring to that driver.")
            if st.button("Delete selected driver", disabled=not confirm_delete):
                deleted = delete_driver(db, chosen_driver)
                if deleted:
                    st.success(f"Deleted driver {chosen_driver}.")
                else:
                    st.warning("Driver was not found.")
                st.rerun()
        else:
            st.info("No drivers registered yet.")

    # TAB 4: simulator and events
    with tabs[3]:
        st.subheader("Generate synthetic telemetry")
        driver_options = list(db.drivers.find({}, {"_id": 0, "driver_id": 1, "name": 1}))
        if not race_ids:
            st.warning("Create a race first.")
        else:
            selected_for_sim = st.selectbox("Race for simulation", race_ids, index=race_ids.index(race_id) if race_id in race_ids else 0, key="sim_race")
            if not driver_options:
                st.warning("Register at least one driver before generating telemetry.")
            else:
                driver_map = {d["driver_id"]: d["name"] for d in driver_options}
                driver_choices = ["Random participating driver"] + [f'{d["driver_id"]} — {d["name"]}' for d in driver_options]
                driver_choice = st.selectbox("Driver", driver_choices)
                event_count = st.number_input("Number of events to generate", min_value=1, max_value=500, value=10, step=1)
                if st.button("Generate telemetry", type="primary"):
                    race_doc = db.races.find_one({"race_id": selected_for_sim})
                    if not race_doc:
                        st.error("Race does not exist.")
                    elif race_doc.get("status") in ("COMPLETED", "ABORTED"):
                        st.error("This race is completed or aborted. Change its status before generating more telemetry.")
                    else:
                        chosen_id = None if driver_choice == "Random participating driver" else driver_choice.split(" — ", 1)[0]
                        created = []
                        try:
                            for _ in range(int(event_count)):
                                created.append(generate_event(db, race_id=selected_for_sim, driver_id=chosen_id))
                            st.success(f"Inserted {len(created)} telemetry events for {selected_for_sim}.")
                            st.dataframe(pd.DataFrame([{k: str(v) if k == "timestamp" else v for k, v in e.items()} for e in created]).drop(columns=["event_id"], errors="ignore"), use_container_width=True)
                        except Exception as exc:
                            st.error(f"Simulation stopped: {exc}")

        st.divider()
        st.subheader("Record a pit stop")
        if race_ids and driver_options:
            with st.form("pit_stop_form", clear_on_submit=True):
                pit_race = st.selectbox("Race", race_ids, key="pit_race")
                pit_driver = st.selectbox("Driver", [d["driver_id"] for d in driver_options], key="pit_driver")
                pit_lap = st.number_input("Lap", min_value=1, max_value=100, value=10)
                pit_duration = st.number_input("Pit-stop duration (seconds)", min_value=1.0, max_value=60.0, value=2.5, step=0.1)
                old_compound = st.selectbox("Old tyre compound", ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"], key="old_compound")
                new_compound = st.selectbox("New tyre compound", ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"], key="new_compound")
                if st.form_submit_button("Save pit stop"):
                    try:
                        db.pit_stops.insert_one({
                            "race_id": pit_race, "driver_id": pit_driver, "lap": int(pit_lap),
                            "duration_seconds": float(pit_duration), "old_compound": old_compound,
                            "new_compound": new_compound, "data_origin": "MANUAL_DEMO",
                            "timestamp": datetime.now(timezone.utc),
                        })
                        st.success("Pit stop saved to MongoDB.")
                    except PyMongoError as exc:
                        st.error(f"Could not save pit stop: {exc}")

        st.subheader("Record an incident")
        if race_ids:
            with st.form("incident_form", clear_on_submit=True):
                incident_race = st.selectbox("Race", race_ids, key="incident_race")
                incident_lap = st.number_input("Incident lap", min_value=1, max_value=100, value=10)
                incident_type = st.selectbox("Incident type", ["SAFETY_CAR", "VIRTUAL_SAFETY_CAR", "RAIN", "CRASH", "DEBRIS", "MECHANICAL"])
                severity = st.selectbox("Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                description = st.text_input("Description", placeholder="Synthetic demonstration incident")
                if st.form_submit_button("Save incident"):
                    try:
                        db.incidents.insert_one({
                            "race_id": incident_race, "lap": int(incident_lap), "type": incident_type,
                            "severity": severity, "description": description.strip() or "Manually entered demo incident",
                            "timestamp": datetime.now(timezone.utc), "data_origin": "MANUAL_DEMO",
                        })
                        st.success("Incident saved to MongoDB.")
                    except PyMongoError as exc:
                        st.error(f"Could not save incident: {exc}")

        st.divider()
        if race_ids:
            st.subheader("Existing pit stops")
            st.dataframe(pd.DataFrame(list(db.pit_stops.find({"race_id": race_id}, {"_id": 0}))), use_container_width=True)
            st.subheader("Existing incidents")
            st.dataframe(pd.DataFrame(list(db.incidents.find({"race_id": race_id}, {"_id": 0}))), use_container_width=True)

except Exception as e:
    st.error("Cannot connect to MongoDB or load the application.")
    st.code(str(e))
    st.markdown("Check `.env`, start MongoDB, then run `python scripts/setup_database.py`.")
finally:
    if client is not None:
        client.close()
