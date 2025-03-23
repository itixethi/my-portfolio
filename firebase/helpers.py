from http.client import NOT_FOUND
from fastapi.responses import HTMLResponse, JSONResponse
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
from google.auth.exceptions import RefreshError

firestore_db = firestore.Client()

# validate a Firebase token
def validateFirebaseToken(id_token, firebase_request_adapter):
    if not id_token:
        return None

    try:
        return google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except Exception:
        return None

# add a driver to Firestore, preventing duplicates
def addDriverHelper(name, age, total_pole_positions, total_race_wins, total_points_scored, total_world_titles, total_fastest_laps, team):
    driver = {
        "Name": name,
        "Age": age,
        "TotalPolePositions": total_pole_positions,
        "TotalRaceWins": total_race_wins,
        "TotalPointsScored": total_points_scored,
        "TotalWorldTitles": total_world_titles,
        "TotalFastestLaps": total_fastest_laps,
        "Team": team
    }
    try:
        existing = firestore_db.collection("drivers").where("Name", "==", name).get()
        if len(existing) > 0:
            return HTMLResponse(f"Driver with name {name} already exists", status_code=500)
        firestore_db.collection("drivers").add(driver)
        return True
    except RefreshError as e:
        return HTMLResponse(str(e), status_code=503)

# get a driver by ID
def getDriverById(id: str):
    try:
        doc = firestore_db.collection('drivers').document(id).get()
        if not doc.exists:
            return {"message": "Driver not found"}
        return {"id": id, **doc.to_dict()}
    except NOT_FOUND as e:
        return JSONResponse(content={"error": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=503)

# get a paginated list of drivers
def getDrivers(count=10, page=1):
    try:
        query = firestore_db.collection('drivers').order_by('Name').offset((page - 1) * count).limit(count)
        return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
    except RefreshError as e:
        return HTMLResponse(str(e), status_code=503)
    return None