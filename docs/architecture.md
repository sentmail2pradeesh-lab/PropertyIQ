# PropertyIQ — Architecture

## The big picture in plain words

Think of PropertyIQ as a photo studio's back office with three kinds of workers:

1. **Fast, deterministic checkers** (OpenCV). Is it blurry? Too dark? An exact copy? These are maths, not AI. They're free, instant and always give the same answer.
2. **Pattern recognisers** (CLIP, Sentence Transformers, small vision models). They turn photos and sentences into lists of numbers called *embeddings*, where "similar meaning" means "numbers close together". That's what lets you search "kitchen with marble countertops" without anyone tagging photos.
3. **A reasoning assistant** (an LLM like Gemini). Reads the client's messy brief, turns it into structured JSON, compares it against what the checkers found, and drafts instructions and reports. It's the most expensive and least predictable worker, so it only gets jobs the others can't do, and a human approves its important outputs.

A **LangGraph agent** is the supervisor that runs these workers in a fixed, inspectable order with checkpoints — not a free-roaming bot.

```
React dashboard  ──HTTP/WebSocket──►  FastAPI (modular monolith)
                                        ├── auth / orgs / projects
                                        ├── uploads ──► object storage (MinIO / S3)
                                        ├── cv service (OpenCV)
                                        ├── embeddings (CLIP, sentence-transformers)
                                        ├── llm gateway (Gemini/OpenAI-compatible, cost + cache)
                                        ├── rag / search
                                        ├── agent (LangGraph, human approval)
                                        └── reports
                                              │ enqueue
                                        Redis ──► Celery workers (heavy jobs)
                                              │
                                        PostgreSQL + pgvector
```

**Why a modular monolith:** one deployable, one database, one codebase — but each folder under `services/` has a clear boundary so it can be split out later if it ever needs to be. Microservices would cost you weeks of infra work that teaches little about AI.

## Rules the code follows

- The API layer is thin: validate → call a service → return a schema.
- Services never import FastAPI. They're plain Python, easy to test and reuse from Celery workers.
- Originals are write-once. Every derived file (preview, resize, crop) is an `asset_variant`.
- Every AI result stores `model_name`, `model_version`, `prompt_version` and the input hash so it can be reproduced, compared and cached.
- An LLM is never the only line of defence: its output is parsed into a Pydantic model and rejected if it doesn't validate.

## Gaps and risks in the original plan

### Domain risks (these matter most — they're real-estate specific)

| Risk | Why it bites | Plan |
|---|---|---|
| **HDR brackets look like "bad" photos** | Real estate shoots are often 3–7 bracketed exposures of the same angle. A naive system flags them as duplicates *and* as under/overexposed. | Group by EXIF capture time + exposure bias into `bracket` groups before duplicate detection. Score the group, not each frame. |
| **Bright windows wreck averages** | A room can have a fine mean brightness while the window is pure white. Your client brief literally says "keep the outdoor view". | Already handled in Day 1: highlight-clipping % is reported separately. Later: window region detection. |
| **EXIF orientation** | Phones/cameras store images sideways with a rotation flag. Classifiers see rotated rooms. | Handled in Day 1 via `ImageOps.exif_transpose`. |
| **Room classification has no ready model** | There's no great off-the-shelf "real estate room" classifier. | Start with CLIP zero-shot (no training). Build a 300–500 image labelled set early; fine-tune a small head on CLIP features only if zero-shot accuracy is poor. |
| **Thresholds are guesses** | Blur = 100 is a common starting point, not truth for your photos. | Milestone 4 builds a labelled evaluation set and tunes thresholds against it. |
| **RAW files are huge** | 40–80 MB each; full demosaicing is slow and RAM-heavy. | Extract the embedded JPEG preview with `rawpy` first (fast); full decode only when needed, in a worker. |

### Technical risks

| Risk | Plan |
|---|---|
| **Celery doesn't officially support Windows**, and Redis has no native Windows build. | Run Redis, Postgres and MinIO in Docker Desktop (WSL2 backend). For local Celery on Windows use `--pool=solo`, or run workers in Docker. Decide at milestone 11. |
| **4 GB VRAM** | CLIP ViT-B/32 (~600 MB in fp16) and sentence-transformers run fine. No local LLMs beyond toy sizes — use an API. Batch embeddings; fall back to CPU. |
| **Client photo privacy on free LLM tiers** | Free API tiers may allow the provider to use your inputs to improve their models. Read the current terms before sending real client photos; use your own/public sample images while on free tier. |
| **Embedding model changes** | Changing CLIP model changes vector dimensions and meaning. Store `model_name` + `dim` per embedding row; re-embed on change. |
| **LLM cost creep** | Central `llm_gateway` that every call goes through: logs tokens + cost, caches by (prompt_version, input hash), enforces per-org budget. |
| **Prompt injection via client briefs** | Briefs are user-written text sent to an LLM. Treat them as data inside delimiters, never as instructions; validate output schema; agent tools have an allowlist. |
| **Scope** | 15 milestones is a lot. Milestones 1–10 form a demoable MVP; 11–15 make it production-grade. |

### Missing pieces added to the design

- **Tables:** `llm_calls` (tokens, cost, latency, model, prompt_version), `prompt_versions`, `brief_requirements` (one row per parsed requirement, so compliance can be checked row by row), `bracket_groups` (or a `group_type` column on `duplicate_groups`), `room_types` (controlled vocabulary).
- **Storage abstraction:** one `StorageService` interface with MinIO locally and S3/R2 in production.
- **Evaluation dataset folder** (`eval/`) started from milestone 4, not left to milestone 13.
- **Structured logging + request IDs** from milestone 5, so worker and API logs can be correlated.
- **Tenant isolation** enforced in a repository layer (every query filtered by `organization_id`); Postgres row-level security as a stretch goal.
