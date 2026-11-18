import os
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.agents import run_workflow

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", "/tmp/agentflow"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "agentflow.db"

app = FastAPI(
    title="AgentFlow AI",
    description="A transparent multi-agent workflow automation MVP.",
    version="1.0.0",
)

# Same-origin frontend/API. CORS is intentionally not opened to arbitrary origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class WorkflowRequest(BaseModel):
    request: str = Field(min_length=5, max_length=2000)

@contextmanager
def db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

def init_db():
    with db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "service": "agentflow-ai"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "database": "sqlite"}

@app.post("/api/workflows", status_code=201)
def create_workflow(body: WorkflowRequest):
    try:
        result = run_workflow(body.request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    with db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO workflows (request, status, payload) VALUES (?, ?, ?)",
            (result["request"], result["status"], json.dumps(result)),
        )
        conn.commit()
        result["id"] = cursor.lastrowid
    return result

@app.get("/api/workflows")
def list_workflows():
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT id, request, status, created_at FROM workflows ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [dict(row) for row in rows]

@app.get("/api/workflows/{workflow_id}")
def get_workflow(workflow_id: int):
    with db_connection() as conn:
        row = conn.execute(
            "SELECT payload FROM workflows WHERE id = ?", (workflow_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return json.loads(row["payload"])

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
