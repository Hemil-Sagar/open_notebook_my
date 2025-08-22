import os
from typing import Optional
from fastapi import HTTPException, Request, responses
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class PasswordAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check password authentication for all API requests.
    Only active when OPEN_NOTEBOOK_PASSWORD environment variable is set.
    """

    def __init__(self, app, excluded_paths: Optional[list]= None):
        super().__init__(app)
        self.password = os.environ.get("OPEN_NOTEBOOK_PASSWORD")
        self.excluded_paths = excluded_paths or ["/", "/health", "/docs", "/openapi.json", "redoc"]

    async def dispatch(self, request: Request, call_next):

        if not self.password:
            return await call_next(request)

        if request.url.path in self.excluded_paths:
            return await call_next(request)


        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail":"Missing authorization header"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        try: 
            schema, credentials= auth_header.split(" ", 1)
            if schema.lower() != "bearer":
                raise ValueError("Invaild authentication scheme")
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid password"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if credentials != self.password:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid password"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        response = await call_next(request)
        return response

security = HTTPBearer(auto_error=False)

def check_api_passwword(credentials: HTTPAuthorizationCredentials = None) -> bool:
    """
    Utility function to check API password.
    Can be used as a dependency in individual reouts if needed.
    """

    password= os.environ.get("OPEN_NOTEBOOK_PASSWORD")

    if not password:
        return True

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization",
            headers={"WWW-Anthenticate":"Bearer"},
        )

    if credentials.credentials != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password",
            headers={"WWW-Authenticate":"Bearer"},
        )