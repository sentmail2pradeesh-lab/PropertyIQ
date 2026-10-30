# PropertyIQ — Roadmap

Each milestone ends with: working code, passing tests, a short note in `docs/`, and a git commit. We move on only when it runs on your machine.

| # | Milestone | GenAI concept you learn | What gets built | Done when |
|---|---|---|---|---|
| 1 | LLM fundamentals | Tokens, context window, next-token prediction, temperature | `learning/day01_tokens.py` | You can explain why a brief costs N tokens |
| 2 | **First image-analysis API** ← *you are here* | When *not* to use an LLM | `POST /api/v1/images/analyze` (blur, exposure, SHA-256) | 14 tests pass, Swagger works |
| 3 | Client brief parser | Prompting, LLM APIs, structured output, validation, retries | `POST /briefs/parse` using Gemini + Pydantic schema; prompt v1 file; cost logging | Brief → valid JSON, bad output rejected |
| 4 | Classification + quality | Zero-shot CLIP, evaluation sets, precision/recall | Room classifier, perceptual-hash duplicates, bracket grouping, labelled `eval/` set | Accuracy measured, thresholds tuned |
| 5 | Postgres + projects | — (backend) | SQLAlchemy 2 models, Alembic, JWT auth, orgs/roles, Docker Compose for Postgres | CRUD + tenant isolation tests |
| 6 | Uploads + RAW | — | Presigned uploads to MinIO, `assets`/`asset_variants`, rawpy previews | Upload 50 photos, originals untouched |
| 7 | Embeddings + image search | Embeddings, cosine similarity, pgvector, HNSW index | CLIP image + text embeddings, `POST /projects/{id}/search` | "kitchen with marble countertops" returns kitchens |
| 8 | RAG + requirement checks | Chunking, retrieval, hybrid search, reranking, grounding | Requirement-vs-asset compliance; LLM answers cite asset IDs | Missing shots detected on test project |
| 9 | LangGraph agent | Tools, state, checkpoints, human-in-the-loop | Agent run: brief → retrieve → analyse → gaps → recommendations → *pause for approval* → report | Run resumes after approval; tools allowlisted |
| 10 | React frontend | — | Vite + TS + Tailwind dashboard: projects, upload, gallery, review | Full flow in the browser |
| 11 | Redis, Celery, WebSockets | — | Background analysis jobs, retries, `/ws/jobs/{id}` progress | 200-image batch with live progress |
| 12 | Reports + analytics | Summarisation with grounding | Quality/compliance/editing reports, token + cost dashboard | PDF/HTML report per project |
| 13 | Testing + evaluation | LLM evaluation, RAG metrics, LLM-as-judge (carefully) | Eval harness, retrieval recall@k, brief-parse accuracy | `eval/report.md` with numbers |
| 14 | Docker + deployment | — | Dockerfiles, GitHub Actions CI, cloud deploy | Public demo URL |
| 15 | Portfolio | — | Architecture diagram, README, demo video, write-up | Ready to send to recruiters |

## Budget plan (target < ₹5,000)

- ₹0: Python, FastAPI, OpenCV, CLIP, sentence-transformers, Postgres, Redis, MinIO, Docker, LangChain/LangGraph — all open source and local.
- ₹0: Gemini API free tier for milestones 3–9 (rate-limited; fine for development). Check current limits and data-use terms when we get there.
- ₹0: Google Colab / Kaggle GPU if we fine-tune anything in milestone 4.
- Paid, only at milestone 14: a small VM or container host + domain. We'll compare options then and pick one that fits the remaining budget.
