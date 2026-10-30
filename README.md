# PropertyIQ

Multimodal AI-powered real estate media intelligence platform. Upload property photos and a client brief; PropertyIQ checks image quality, understands the brief, finds gaps and drafts editing instructions and reports for human review.

**Status:** Milestone 2 — first FastAPI image-analysis API (blur + exposure).

## Repository layout

```
propertyiq/
├── backend/                 FastAPI app (Python 3.12)
│   ├── app/
│   │   ├── main.py          App factory, CORS, router mount
│   │   ├── core/config.py   All settings, read from env / .env
│   │   ├── api/v1/          Versioned HTTP layer (thin: validate, call service, respond)
│   │   │   └── routes/      health.py, images.py
│   │   ├── schemas/         Pydantic request/response models (the API contract)
│   │   └── services/        Business logic, no HTTP code
│   │       ├── image_loader.py   Safe decoding, EXIF rotation, SHA-256
│   │       └── image_quality.py  Blur + exposure (OpenCV)
│   ├── tests/               pytest unit + API tests (synthetic images)
│   ├── requirements.txt
│   └── requirements-dev.txt
├── learning/                Small scripts that teach one concept each
├── docs/                    Architecture, roadmap, daily notes
├── frontend/                React + Vite + TS (milestone 10)
├── infra/                   Docker Compose, CI (from milestone 5)
└── .env.example
```

Later milestones add `app/db/`, `app/workers/`, `app/agents/`, `app/llm/` and `alembic/` inside `backend/` — see [docs/roadmap.md](docs/roadmap.md).

## Run it on Windows (PowerShell)

Install **Python 3.12** from python.org (tick "Add python.exe to PATH"). 3.12 is the safest choice for PyTorch/CUDA wheels later.

```powershell
cd propertyiq\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
copy ..\.env.example .env

uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs, expand **POST /api/v1/images/analyze**, click *Try it out*, choose a photo, *Execute*.

Or from a second terminal:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/images/analyze -F "file=@C:\path\to\photo.jpg"
```

(Use `curl.exe`, not `curl` — in PowerShell `curl` is an alias for a different command.)

### Tests and lint

```powershell
python -m pytest -v
ruff check .
ruff format .
```

### Day 1 learning script

```powershell
python ..\learning\day01_tokens.py
```

## Docs

- [Architecture and risks](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Day 1 — LLM fundamentals](docs/day01-llm-fundamentals.md)
