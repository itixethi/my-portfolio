from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken, addDriverHelper, getDriverById
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# this view shows the form to add a new driver
async def addDriverFormView(request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    if not user_token:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("add_driver.html", {"request": request, "isAuthorized": True})

# this handles the post request to add a new driver
async def addDriverPost(request: Request):
    form = await request.form()

    result = addDriverHelper(
        name=form.get("name"),
        age=int(form.get("age")),
        total_pole_positions=int(form.get("total_pole_positions")),
        total_race_wins=int(form.get("total_race_wins")),
        total_points_scored=int(form.get("total_points_scored")),
        total_world_titles=int(form.get("total_world_titles")),
        total_fastest_laps=int(form.get("total_fastest_laps")),
        team=form.get("team")
    )

    if result is not True:
        return result  # error response from addDriverHelper

    return RedirectResponse(url="/", status_code=302)

# this displays a single driver's information
async def viewDriverInfo(driver_id: str, request: Request, templates: Jinja2Templates):
    driver = getDriverById(driver_id)
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    return templates.TemplateResponse("driverInfo.html", {"request": request, "driver": driver, "isAuthorized": isAuthorized})

# this deletes a driver from the database
async def deleteDriver(request: Request):
    form = await request.form()
    id = form.get("id")
    try:
        firestore_db.collection("drivers").document(id).delete()
        return RedirectResponse("/", status_code=302)
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

# this updates an existing driver's details
async def updateDriver(request: Request):
    form = await request.form()
    id = form.get("id")
    updated_data = {
        "Name": form.get("name"),
        "Age": int(form.get("age")),
        "TotalPolePositions": int(form.get("total_pole_positions")),
        "TotalRaceWins": int(form.get("total_race_wins")),
        "TotalPointsScored": int(form.get("total_points_scored")),
        "TotalWorldTitles": int(form.get("total_world_titles")),
        "TotalFastestLaps": int(form.get("total_fastest_laps")),
        "Team": form.get("team")
    }
    try:
        firestore_db.collection("drivers").document(id).update(updated_data)
        return RedirectResponse("/driver-info/" + id, status_code=302)
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)
    
async def editDriverFormView(driver_id: str, request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    driver_doc = firestore_db.collection("drivers").document(driver_id).get()
    if not driver_doc.exists:
        return HTMLResponse("Driver not found.", status_code=404)

    driver = {"id": driver_id, **driver_doc.to_dict()}
    return templates.TemplateResponse("edit_driver.html", {
        "request": request,
        "isAuthorized": isAuthorized,
        "driver": driver
    })