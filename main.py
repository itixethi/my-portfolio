from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status

# i call the app i shall use here 
app = FastAPI()
firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()

# i set the static and templates folders here 
app.get("/")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def getUser(user_token):
    user = firestore_db.collection("users").document(user_token['user_id'])
    if not user.get().exists:
        user_data = {"name": "No name", "age": 0}

        user.set(user_data)
        return user