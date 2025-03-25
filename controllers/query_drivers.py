from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# Controller for querying drivers by attribute
async def queryDrivers(request: Request, templates: Jinja2Templates):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None

    attribute = request.query_params.get("attribute")
    operator = request.query_params.get("operator")
    value = request.query_params.get("value")
    drivers = []

    if attribute and operator and value:
        try:
            numeric_value = int(value)
            collection_ref = firestore_db.collection("drivers")

            if operator == "eq":
                query_ref = collection_ref.where(attribute, "==", numeric_value)
            elif operator == "gt":
                query_ref = collection_ref.where(attribute, ">", numeric_value)
            elif operator == "lt":
                query_ref = collection_ref.where(attribute, "<", numeric_value)
            else:
                query_ref = collection_ref

            drivers = [{"id": doc.id, **doc.to_dict()} for doc in query_ref.stream()]

        except Exception as e:
            return HTMLResponse(f"Query failed: {str(e)}", status_code=500)

    return templates.TemplateResponse("query_drivers.html", {
        "request": request,
        "isAuthorized": isAuthorized,
        "drivers": drivers,
        "query_submitted": attribute is not None
    })