from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# this searches drivers by name or a stat range
async def searchDriverPost(request: Request, templates: Jinja2Templates):
    try:
        # Check login status
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None

        # Get query parameters
        search_by = request.query_params.get("by", "")
        search = request.query_params.get("search", "")
        min_value = request.query_params.get("min", "0")
        max_value = request.query_params.get("max", "9999")

        # Fetch drivers based on query
        if search_by == "Name" and search:
            stream = firestore_db.collection("drivers").where("Name", "==", search).stream()
        elif search_by and min_value and max_value:
            try:
                min_val = int(min_value)
                max_val = int(max_value)
                stream = firestore_db.collection("drivers").where(search_by, ">=", min_val).where(search_by, "<=", max_val).stream()
            except ValueError:
                return HTMLResponse("Invalid numeric range.", status_code=400)
        else:
            stream = firestore_db.collection("drivers").stream()

        drivers = [{"id": doc.id, **doc.to_dict()} for doc in stream]
        return templates.TemplateResponse("search_drivers.html", {
            "request": request,
            "isAuthorized": isAuthorized,
            "drivers": drivers,
            "search": search
        })
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

# this searches teams by name or a stat range
async def searchTeamPost(request: Request, templates: Jinja2Templates):
    try:
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None

        search_by = request.query_params.get("by", "")
        search = request.query_params.get("search", "")
        min_value = request.query_params.get("min", "0")
        max_value = request.query_params.get("max", "9999")

        if search_by == "Name":
            stream = firestore_db.collection("teams").where("Name", "==", search).stream()
        elif search_by:
            stream = firestore_db.collection("teams").where(search_by, ">=", int(min_value)).where(search_by, "<=", int(max_value)).stream()
        else:
            stream = firestore_db.collection("teams").stream()

        teams = [{"id": doc.id, **doc.to_dict()} for doc in stream]
        return templates.TemplateResponse("search_teams.html", {"request": request, "isAuthorized": isAuthorized, "teams": teams, "search": search })
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)