from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import (
    auth, profile, analyze, resume, cover_letter, company, interview,
    sponsorship, networking, tracker, dashboard, events, strategy,
    jobs, discovery,
)

app = FastAPI(title="CareerOS API", version="1.0.0",
              description="AI job-application copilot for international students.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "ai": "openai" if settings.openai_api_key else "mock"}


for r in (auth, profile, analyze, resume, cover_letter, company, interview,
          sponsorship, networking, tracker, dashboard, events, strategy,
          jobs, discovery):
    app.include_router(r.router)
