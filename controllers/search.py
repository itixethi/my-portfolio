from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status
from google.cloud import firestore
from google.auth.transport import requests

#importinf helper functions from firebase
from firebase.helpers import validateFirebaseToken

# initializing Firestore client and firebase request adapter 
firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()

async def 