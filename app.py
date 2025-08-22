import os
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials

# Set a test password
os.environ["OPEN_NOTEBOOK_PASSWORD"] = "mypassword"

app = FastAPI()

# Import your middleware
from api.routers.auth import PasswordAuthMiddleware, check_api_passwword

# Add middleware
app.add_middleware(PasswordAuthMiddleware)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/secure")
async def secure_route(credentials: HTTPAuthorizationCredentials = Depends(check_api_passwword)):
    return {"message": "You passed the password check!"}
