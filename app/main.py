from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.routes import auth, user, admin
from app.models import user as user_models, token as token_models, audit as audit_models

# Create DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Auth Service",
    description="Centralized Authentication and Authorization Service with RBAC, JWT, and Rate Limiting",
    version="1.0.0"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}
