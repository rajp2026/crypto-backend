from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api import auth_routes
from app.api import market_routes
from app.api.ws_routes import router as ws_router

app = FastAPI()

# Allow both origin formats (with and without trailing slash just in case)
# and use generic headers to avoid pre-flight rejection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(market_routes.router)
app.include_router(ws_router)

@app.get('/')
def home(db: Session = Depends(get_db)):
    return {
        "message": "Welcome to Crypto exchange Platform"
    }

# All market listeners and stream services are now decoupled.
# WebSocket data is bridged per-connection in app/api/ws_routes.py