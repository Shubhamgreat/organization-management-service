from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import db
from .api import organization, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect_db()
    print("Application started successfully")
    yield
    await db.close_db()
    print("Application shutdown completed")


app = FastAPI(
    title="Organization Management Service",
    description="Multi-tenant organization management system with MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organization.router)
app.include_router(admin.router)


@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "healthy",
        "message": "Organization Management Service is running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "service": "operational",
    }
