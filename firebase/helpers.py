from fastapi.responses import HTMLResponse, JSONResponse
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status
from google.auth.exceptions import RefreshError

firestore_db = firestore.Client()

def validateFirebaseToken(id_token, firebase_request_adapter):
    if not id_token:
        return None
    
    user_token = None

    try:
        user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except Exception as e:
        user_token = None
    
    return user_token