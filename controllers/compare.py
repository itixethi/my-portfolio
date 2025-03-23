from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# compare drivers form
async def compareDriversView(request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    drivers = [{"id": doc.id, **doc.to_dict()} for doc in firestore_db.collection("drivers").stream()]
    error = request.query_params.get("error")

    driver1_id = request.query_params.get("driver1")
    driver2_id = request.query_params.get("driver2")
    driver1 = driver2 = None

    if driver1_id and driver2_id:
        driver1_doc = firestore_db.collection("drivers").document(driver1_id).get()
        driver2_doc = firestore_db.collection("drivers").document(driver2_id).get()
        if driver1_doc.exists and driver2_doc.exists:
            driver1 = {"id": driver1_id, **driver1_doc.to_dict()}
            driver2 = {"id": driver2_id, **driver2_doc.to_dict()}

    return templates.TemplateResponse("compare_drivers.html", {
        "request": request,
        "isAuthorized": isAuthorized,
        "drivers": drivers,
        "driver1": driver1,
        "driver2": driver2,
        "error": error
    })

# process driver form
async def compareDriversPost(request: Request):
    form = await request.form()
    driver1_id = form.get("driver1")
    driver2_id = form.get("driver2")

    if driver1_id == driver2_id:
        return RedirectResponse(url="/compare-drivers?error=same", status_code=302)

    return RedirectResponse(url=f"/compare-drivers?driver1={driver1_id}&driver2={driver2_id}", status_code=302)

async def compareDriversResult(request: Request, templates: Jinja2Templates):
    return await compareDriversView(request=request, templates=templates)