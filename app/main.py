from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api import auth_routes
from app.api import market_routes
from app.api.ws_routes import router as ws_router
from app.services.market.market_stream_service import MarketStreamService
import asyncio
from app.services.market.market_pubsub_listener import MarketPubSubListener

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(market_routes.router)
app.include_router(ws_router)

@app.get('/')
def home(db: Session = Depends(get_db)):
    return{
        "message": "Welcome to Crypto exchange Platform"
    }

# @app.on_event("startup")
# async def start_market_stream():

#     print("Starting Market Stream Service...")

#     service = MarketStreamService()

#     asyncio.create_task(service.start())

@app.on_event("startup")
async def start_market_listener():

    listener = MarketPubSubListener()

    asyncio.create_task(listener.start())