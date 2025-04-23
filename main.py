import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routers import router as api_router  # Import the router
from api.dependencies import get_db
from sqlalchemy.orm import Session
from core.database import create_db_and_tables
from utils.logging import logger


app = FastAPI(
    title="CounselAI-Pro",
    version="0.1.0",
    description="A world-class legal contract analysis microservice.",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Use configured origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Startup event: create database tables.
    """
    logger.info("Starting up...")
    create_db_and_tables()  # Create tables if they don't exist
    logger.info("Database tables created (if needed).")


@app.get("/")
async def root():
    return {"project": "CounselAI-Pro", "version": "0.1.0"}


app.include_router(api_router)  # Include the API router

# Example Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTPException: {exc.detail} (status code: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
