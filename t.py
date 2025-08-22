from fastapi import FastAPI
from api.routers.auth import PasswordAuthMiddleware  # import from your auth.py

app = FastAPI()

# Add your middleware
app.add_middleware(PasswordAuthMiddleware)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/secure")
async def secure():
    return {"message": "You are authorized!"}
