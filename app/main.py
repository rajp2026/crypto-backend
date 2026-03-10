from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api import auth_routes

app = FastAPI()

app.include_router(auth_routes.router)

@app.get('/')
def home(db: Session = Depends(get_db)):
    return{
        "message": "Welcome to Crypto exchange Platform"
    }