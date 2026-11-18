# AgentFlow AI

A deployable multi-agent workflow automation MVP built with FastAPI, Python, HTML, CSS and JavaScript.

## What it does

- Planner Agent converts a request into structured steps.
- Execution Agent runs and records each step in this MVP workflow.
- Review Agent verifies that every planned step completed.
- FastAPI persists workflow records in SQLite.
- Responsive dashboard displays results and recent activity.

**Transparency:** The initial version uses deterministic Python agents. It does not call an external LLM or execute arbitrary commands. The execution agent records safe workflow steps; it is not an autonomous system that performs actions in third-party services.

## Run locally (Windows PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Test

```powershell
pytest -q
```

## Deploy to Google Cloud Run

Prerequisites: a Google Cloud project with billing enabled, Cloud Run and Cloud Build permissions, and Google Cloud CLI installed and authenticated.

```powershell
gcloud auth login
gcloud projects list
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
gcloud run deploy agentflow-ai --source . --region asia-south1 --allow-unauthenticated
```

The deployment command prints the service URL. Open that exact URL and check `/health`.

## Important deployment note

Cloud Run's local filesystem is ephemeral. This demo stores its SQLite database under `/tmp`; workflow history may be lost when instances restart or scale. For durable production data, use Cloud SQL or another managed database. Do not store secrets in source code. Add authentication and authorization before exposing sensitive workflows.

## API

- `GET /health`
- `GET /api/health`
- `POST /api/workflows` with JSON `{"request":"Prepare a weekly project report"}`
- `GET /api/workflows`
- `GET /api/workflows/{id}`
- Interactive API documentation: `/docs`
