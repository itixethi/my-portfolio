from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
from google.auth.exceptions import RefreshError

from controllers.search import globalSearch
from firebase.helpers import validateFirebaseToken
from controllers.login import login
from controllers.driver import addDriverFormView, addDriverPost, viewDriverInfo, deleteDriver, updateDriver
from controllers.team import addTeamFormView, addTeamPost, viewTeamInfo, deleteTeam, updateTeam
from controllers.compare import compareDriversView, compareDriversPost, compareDriversResult
from controllers.compare_teams import compareTeamsView, compareTeamsPost, compareTeamsResult
from controllers.driver import editDriverFormView
from controllers.query_teams import queryTeams

# i call the app i shall use for my routing
app = FastAPI()
firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()

# i define static and template directories 
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# This retrieves a user document from Firestore using the Firebase user ID.
# If the user doesn't exist in the "users" collection, it initializes a default entry.
def getUser(user_token):
    user = firestore_db.collection("users").document(user_token['user_id'])
    if not user.get().exists:
        user_data = {"name": "No name", "age": 0}
        user.set(user_data)
    return user

# This validates an ID token and returns the corresponding user document from Firestore.
# If the token is invalid or missing, returns None.
def checkAndReturnUser(id_token):
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    return getUser(user_token) if user_token else None

# Home route handler, this displays homepage with all drivers and teams.
# Also determines if the user is logged in by checking for a valid Firebase token.
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None

        drivers = list(firestore_db.collection("drivers").stream())
        teams = list(firestore_db.collection("teams").stream())
        drivers_data = [{"id": d.id, **d.to_dict()} for d in drivers]
        teams_data = [{"id": t.id, **t.to_dict()} for t in teams]

        return templates.TemplateResponse("index.html", {"request": request, "isAuthorized": isAuthorized, "drivers": drivers_data, "teams": teams_data})
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def handleLoginRoute(request: Request):
    return await login(request=request, templates=templates)

@app.get("/add-driver", response_class=HTMLResponse)
async def addDriverForm(request: Request):
    return await addDriverFormView(request=request, templates=templates)

@app.post("/add-driver", response_class=RedirectResponse)
async def handleAddDriverPost(request: Request):
    return await addDriverPost(request=request)

@app.post("/update-driver", response_class=RedirectResponse)
async def handleUpdateDriver(request: Request):
    return await updateDriver(request=request)

@app.post("/delete-driver", response_class=RedirectResponse)
async def handleDeleteDriver(request: Request):
    return await deleteDriver(request=request)

@app.get("/add-team", response_class=HTMLResponse)
async def addTeamForm(request: Request):
    return await addTeamFormView(request=request, templates=templates)

@app.post("/add-team", response_class=RedirectResponse)
async def handleAddTeamPost(request: Request):
    return await addTeamPost(request=request)

@app.post("/update-team", response_class=RedirectResponse)
async def handleUpdateTeam(request: Request):
    return await updateTeam(request=request)

@app.post("/delete-team", response_class=RedirectResponse)
async def handleDeleteTeam(request: Request):
    return await deleteTeam(request=request)

@app.get("/search", response_class=HTMLResponse)
async def handleGlobalSearch(request: Request):
    return await globalSearch(request=request, templates=templates)

@app.get("/query-teams", response_class=HTMLResponse)
async def handleQueryTeams(request: Request):
    return await queryTeams(request=request, templates=templates)

@app.get("/driver-info/{driver_id}", response_class=HTMLResponse)
async def driverInfo(request: Request, driver_id: str):
    return await viewDriverInfo(driver_id=driver_id, request=request, templates=templates)

@app.get("/driver-info/{driver_id}/edit", response_class=HTMLResponse)
async def editDriverForm(request: Request, driver_id: str):
    return await editDriverFormView(driver_id=driver_id, request=request, templates=templates)

@app.get("/team-info/{team_id}", response_class=HTMLResponse)
async def teamInfo(request: Request, team_id: str):
    return await viewTeamInfo(team_id=team_id, request=request, templates=templates)

@app.get("/compare-drivers", response_class=HTMLResponse)
async def compareDrivers(request: Request):
    return await compareDriversView(request=request, templates=templates)

@app.post("/compare-drivers", response_class=RedirectResponse)
async def handleCompareDrivers(request: Request):
    return await compareDriversPost(request=request)

@app.get("/compare-drivers-result", response_class=HTMLResponse)
async def compareDriversResultRoute(request: Request):
    return await compareDriversResult(request=request, templates=templates)

@app.get("/compare-teams", response_class=HTMLResponse)
async def compareTeams(request: Request):
    return await compareTeamsView(request=request, templates=templates)

@app.post("/compare-teams", response_class=RedirectResponse)
async def handleCompareTeams(request: Request):
    return await compareTeamsPost(request=request)

@app.get("/compare-teams-result", response_class=HTMLResponse)
async def compareTeamsResultRoute(request: Request):
    return await compareTeamsResult(request=request, templates=templates)