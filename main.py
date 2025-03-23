from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status

from firebase.helpers import validateFirebaseToken
from controllers.login import validateFirebaseToken
from controllers.search import perform_driver_query, perform_team_query

# i call the app i shall use here 
app = FastAPI()
firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()

# i set the static and templates folders here 
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def getUser(user_token):
    user = firestore_db.collection("users").document(user_token['user_id'])
    if not user.get().exists:
        user_data = {"name": "No name", "age": 0}

        user.set(user_data)
        return user
    
def checkAndReturnUser(id_token):
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    if not user_token:
        return None
    
    return getUser(user_token)

app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None

        drivers = list(firestore_db.collection("drivers").stream())
        teams = list(firestore_db.collection("teams").stream())
        drivers_data = [{"id": d.id, **d.to_dict()} for d in drivers]
        teams_data = [{"id": t.id, **t.to_dict()} for t in teams]

        return templates.TemplateResponse(request=request, name="index.html", context={"isAuthorized": isAuthorized, "request": request, "drivers": drivers_data, "teams": teams_data})
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)
    
@app.get("/login", response_class=HTMLResponse)
async def handleLoginRoute(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "isAuthorized": False})
    #return await login(request=request, templates=templates)

@app.get("/add-driver", response_class=HTMLResponse)
async def add_driver_form(request: Request):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    if not user_token:
        return RedirectResponse(url="/login", status_code=302)
    return render_user_token(request, user_token, "add_driver.html")

@app.post("/add-driver")
async def add_driver(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    total_poles: int = Form(...),
    total_wins: int = Form(...),
    total_points: int = Form(...),
    total_titles: int = Form(...),
    total_fastest_laps: int = Form(...),
    team: str = Form(...)
):
    driver_data = {
        "Name": name, 
        "Age": age,
        "TotalPolePositions": total_poles,
        "TotalRaceWins": total_wins,
        "TotalPointsScored": total_points,
        "TotalWorldTitles": total_titles,
        "TotalFastestLaps": total_fastest_laps,
        "Team": team
    }
    firestore_db.collection("drivers").add(driver_data)
    return RedirectResponse(url="/", status_code=302)

@app.get("/add-team", response_class=HTMLResponse)
async def add_team_form(request: Request):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    if not user_token:
        return RedirectResponse(url="/login", status_code=302)
    return render_user_token(request, user_token, "add_team.html")

@app.post("/add-team")
async def add_team(
    request: Request,
    name: str = Form(...),
    year_founded: int = Form(...),
    total_poles: int = Form(...),
    total_wins: int = Form(...),
    constructor_titles: int = Form(...),
    last_finish_position: int = Form(...)
):
    team_data = {
        "Name": name,
        "YearFounded": year_founded,
        "TotalPolePositions": total_poles,
        "TotalRaceWins": total_wins,
        "TotalConstructorTitles": constructor_titles,
        "LastSeasonFinish": last_finish_position
    }
    firestore_db.collection("teams").add(team_data)
    return RedirectResponse(url="/", status_code=302)

@app.get("/search-drivers", response_class=HTMLResponse)
async def search_drivers(request: Request, attr: str = "", op: str = "", value: str = ""):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    results = perform_driver_query("drivers", attr, op, value)
    return render_user_token(request, user_token, "search_driver.html", drivers=results, search=attr)

@app.get("/search-teams", response_class=HTMLResponse)
async def search_teams(request: Request, attr: str = "", op: str = "", value: str = ""):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    results = perform_team_query("teams", attr, op, value)
    return render_user_token(request, user_token, "search_team.html", teams=results, search=attr)