from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests
from google.cloud import firestore

# Firebase and Firestore clients
firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# Controller for querying teams by attribute
async def queryTeams(request: Request, templates: Jinja2Templates):
    # Retrieve Firebase token from cookies
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
    isAuthorized = user_token is not None  # check if the user is authenticated

    # Extract query parameters from the URL
    attribute = request.query_params.get("attribute")
    operator = request.query_params.get("operator")
    value = request.query_params.get("value")
    teams = []  # List to hold matched teams

    # Execute query if all parameters are present
    if attribute and operator and value:
        try:
            numeric_value = int(value)  # Convert value to integer
            collection_ref = firestore_db.collection("teams")

            # Build the query based on the operator
            if operator == "eq":
                query_ref = collection_ref.where(attribute, "==", numeric_value)
            elif operator == "gt":
                query_ref = collection_ref.where(attribute, ">", numeric_value)
            elif operator == "lt":
                query_ref = collection_ref.where(attribute, "<", numeric_value)
            else:
                query_ref = collection_ref

            # Fetch results from Firestore
            teams = [{"id": doc.id, **doc.to_dict()} for doc in query_ref.stream()]

        except Exception as e:
            return HTMLResponse(f"Query failed: {str(e)}", status_code=500)

    # Render the results in the template
    return templates.TemplateResponse("query_teams.html", {
        "request": request,
        "isAuthorized": isAuthorized,
        "teams": teams,
        "query_submitted": attribute is not None  # Used to show empty result message
    })