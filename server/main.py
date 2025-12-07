from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.routes import otp_routes, auth_routes, profile_routes, group_routes, activity_routes, crack_routes

import app.models 

app = FastAPI(title="Cracktify API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(otp_routes.router, prefix="/otp", tags=["OTP"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(profile_routes.router, prefix="/profile", tags=["Profile"])
app.include_router(group_routes.router, prefix="/groups", tags=["Groups"])
app.include_router(activity_routes.router, prefix="/activities", tags=["Activities"])
app.include_router(crack_routes.router, prefix="/cracks", tags=["Cracks"])