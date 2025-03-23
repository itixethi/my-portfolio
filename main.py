from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status

from firebase.helpers import validateFirebaseToken

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

        return templates.TemplateResponse(request=request, name="index.html", context={"isAuthorized": isAuthorized, "request": request, })
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)
    
@app.get("/login", response_class=HTMLResponse)
async def handleLoginRoute(request: Request):
    return await login(request=request, templates=templates)
