from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "NyayaSetu is a source-grounded legal-aid and public-service "
        "grievance assistant using RAG over official documents."
    ),
    version="0.1.0",
    debug=settings.app_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "NyayaSetu backend is running.",
        "docs": "/docs",
        "health": "/health",
        "chat": "/chat",
    }