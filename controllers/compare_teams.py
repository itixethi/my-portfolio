from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# compare teams form
async def compareTeamsView(request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    teams = [{"id": doc.id, **doc.to_dict()} for doc in firestore_db.collection("teams").stream()]
    error = request.query_params.get("error")

    return templates.TemplateResponse("compare_teams.html", {
        "request": request,
        "isAuthorized": isAuthorized,
        "teams": teams,
        "error": error
    })

# process team form
async def compareTeamsPost(request: Request):
    form = await request.form()
    team1_id = form.get("team1")
    team2_id = form.get("team2")

    if team1_id == team2_id:
        return RedirectResponse(url="/compare-teams?error=same", status_code=302)

    return RedirectResponse(url=f"/compare-teams-result?team1={team1_id}&team2={team2_id}", status_code=302)

# result view for teams
async def compareTeamsResult(request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    team1_id = request.query_params.get("team1")
    team2_id = request.query_params.get("team2")

    team1_doc = firestore_db.collection("teams").document(team1_id).get()
    team2_doc = firestore_db.collection("teams").document(team2_id).get()
    

    if not team1_doc.exists or not team2_doc.exists:
        return HTMLResponse("One or both teams not found.", status_code=404)

    team1 = {"id": team1_id, **team1_doc.to_dict()}
    team2 = {"id": team2_id, **team2_doc.to_dict()}
    teams = [{"id": doc.id, **doc.to_dict()} for doc in firestore_db.collection("teams").stream()]

    return templates.TemplateResponse("compare_teams.html", {
        "request": request,
        "isAuthorized": isAuthorized,
        "team1": team1,
        "team2": team2,
        "teams": teams
    })