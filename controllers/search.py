from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# combined search route for both drivers and teams
async def globalSearch(request: Request, templates: Jinja2Templates):
    try:
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None

        query = request.query_params.get("query", "").strip()

        if not query:
            return templates.TemplateResponse("search_results.html", {
                "request": request,
                "isAuthorized": isAuthorized,
                "query": query,
                "drivers": [],
                "teams": []
            })

        # Search both drivers and teams collections by Name
        driver_stream = firestore_db.collection("drivers").where("Name", "==", query).stream()
        team_stream = firestore_db.collection("teams").where("Name", "==", query).stream()

        drivers = [{"id": doc.id, **doc.to_dict()} for doc in driver_stream]
        teams = [{"id": doc.id, **doc.to_dict()} for doc in team_stream]

        return templates.TemplateResponse("search_results.html", {
            "request": request,
            "isAuthorized": isAuthorized,
            "query": query,
            "drivers": drivers,
            "teams": teams
        })

    except Exception as e:
        return HTMLResponse(str(e), status_code=500)
