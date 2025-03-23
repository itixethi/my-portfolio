from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# this view shows the form to add a new team
async def addTeamFormView(request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    if not user_token:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("add_team.html", {"request": request, "isAuthorized": True})

# this handles the post request to add a new team
async def addTeamPost(request: Request):
    form = await request.form()

    name = form.get("name").strip()
    name_lower = name.lower()

    team_data = {
        "Name": name,
        "NameLower": name_lower,
        "YearFounded": int(form.get("year_founded")),
        "TotalPolePositions": int(form.get("total_pole_positions")),
        "TotalRaceWins": int(form.get("total_race_wins")),
        "TotalConstructorTitles": int(form.get("total_constructor_titles")),
        "LastSeasonFinish": int(form.get("last_season_finish"))
    }

    try:
        existing = firestore_db.collection("teams").where("NameLower", "==", name_lower).get()
        if existing:
            return HTMLResponse(f"Team named '{name}' already exists.", status_code=400)

        firestore_db.collection("teams").add(team_data)
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

# this displays a single team's information
async def viewTeamInfo(team_id: str, request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    try:
        doc = firestore_db.collection("teams").document(team_id).get()
        if not doc.exists:
            return HTMLResponse("Team not found", status_code=404)

        team = {"id": team_id, **doc.to_dict()}
        return templates.TemplateResponse("teamInfo.html", {"request": request, "team": team, "isAuthorized": isAuthorized})
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

# this deletes a team from the database
async def deleteTeam(request: Request):
    form = await request.form()
    id = form.get("id")
    try:
        firestore_db.collection("teams").document(id).delete()
        return RedirectResponse("/", status_code=302)
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

# this updates an existing team's details
async def updateTeam(request: Request):
    form = await request.form()
    id = form.get("id")

    try:
        # Normalize the updated name
        updated_name = form.get("name").strip()
        updated_name_lower = updated_name.lower()

        # Check for duplicate team name (excluding current team)
        existing_query = firestore_db.collection("teams").where("NameLower", "==", updated_name_lower).stream()
        for doc in existing_query:
            if doc.id != id:
                return HTMLResponse(f"Another team named '{updated_name}' already exists.", status_code=400)

        updated_data = {
            "Name": updated_name,
            "NameLower": updated_name_lower,
            "YearFounded": int(form.get("year_founded")),
            "TotalPolePositions": int(form.get("total_pole_positions")),
            "TotalRaceWins": int(form.get("total_race_wins")),
            "TotalConstructorTitles": int(form.get("total_constructor_titles")),
            "LastSeasonFinish": int(form.get("last_season_finish"))
        }

        firestore_db.collection("teams").document(id).update(updated_data)
        return RedirectResponse("/team-info/" + id, status_code=302)

    except Exception as e:
        return HTMLResponse(str(e), status_code=500)