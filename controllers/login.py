from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase.helpers import validateFirebaseToken
from google.auth.transport import requests

firebase_request_adapter = requests.Request()

async def login(request: Request, templates: Jinja2Templates):
    try:
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None

        return templates.TemplateResponse(request=request, name="login.html", context={"isAuthorized": isAuthorized, "request": request})
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)