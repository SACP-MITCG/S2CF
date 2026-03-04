# BAC - Business Analysis Copilot

BAC is the upstream tool in the SACP ecosystem that creates **Business Use Case Descriptions** with embedded **Business Architecture Model (BAM)** references. Its output feeds into SAC (Solution Architecture Copilot) which generates solution architecture and deployable artifacts.

## Features

- **AI-Assisted Authoring**: Upload business documents, get template suggestions, and AI-generated content
- **Blueprint Templates**: Pre-defined templates for regulatory changes, process improvements, new capabilities, and integrations
- **HOPEX Integration**: Link sections to architecture elements in Bizzdesign HOPEX
- **5-Step Workflow with HITL Review**: Kanban-style workflow with human-in-the-loop approval gates
- **Multiple Export Formats**: Markdown, Word, and IRM JSON-LD (for SAC handover)

---

## Getting Started

### Prerequisites

| Dependency | Required | Notes |
|------------|----------|-------|
| Python 3.11+ | Yes | Backend runtime |
| Node.js 18+ | Yes | Frontend dev server |
| PostgreSQL | Yes | Default: `sacp:localdev@localhost:5432/sacp` |
| OpenAI API key | No | Falls back gracefully — AI features disabled |
| HOPEX API access | No | Falls back to mock data |

### Launch with Docker (easiest)

```bash
cp .env.example .env          # edit with your keys (optional)
docker-compose up --build     # everything on http://localhost:5001
```

### Launch for Development

**1. Backend** (terminal 1):

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit with your keys (optional)
python run.py                 # API on http://localhost:5001
```

**2. Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev                   # UI on http://localhost:5173
```

CORS is pre-configured — the frontend at `:5173` proxies API calls to `:5001`.

### Frontend Only (no backend)

```bash
cd frontend && npm install && npm run dev
```

The UI loads and renders, but API calls will fail gracefully with placeholder states and info toasts.

---

## Project Structure

```
bac/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── extensions.py            # Shared SQLAlchemy instance
│   ├── models/
│   │   ├── irm.py               # IRM domain model (UseCase, Section, BAMReference)
│   │   ├── usecase_db.py        # UseCaseModel (active — used by all routes)
│   │   └── workflow.py          # Workflow + WorkflowStep models
│   ├── routes/
│   │   ├── usecases.py          # Use case CRUD
│   │   ├── workflow.py          # Workflow lifecycle (create, execute, review, advance)
│   │   ├── state.py             # IRM state transitions
│   │   ├── upload.py            # Document upload + extraction
│   │   ├── hopex.py             # HOPEX integration (read-only)
│   │   ├── export.py            # Export (Markdown, Word, IRM JSON-LD)
│   │   └── pages.py             # SPA page serving
│   └── utilities/
│       ├── extractor.py         # Document text extraction
│       ├── templates.py         # Blueprint templates
│       ├── ai_helper.py         # OpenAI integration
│       ├── export_handlers.py   # Export format handlers
│       └── hopex/client.py      # HOPEX GraphQL client (mock fallback)
├── frontend/
│   └── src/
│       ├── types/
│       │   ├── irm.ts           # Domain types
│       │   └── workflow.ts      # Workflow + HITL types
│       ├── context/
│       │   ├── ToastContext.tsx  # Notifications
│       │   ├── UseCaseContext.tsx# Use case CRUD state
│       │   ├── WorkflowContext.tsx # Workflow API + graceful fallback
│       │   └── HopexContext.tsx  # HOPEX connection + link/unlink
│       ├── components/
│       │   ├── Layout.tsx       # App shell, sidebar, drag-drop upload
│       │   ├── StatusBadge.tsx  # Shared status indicator
│       │   ├── SectionSidebar.tsx
│       │   ├── SectionEditor.tsx# Markdown editing + BAM reference display
│       │   ├── HopexPanel.tsx   # HOPEX element browser + linking
│       │   ├── ExportMenu.tsx   # Export dropdown (MD, Word, IRM, SAC send)
│       │   ├── WorkflowStepper.tsx # 5-step Kanban bar
│       │   └── ReviewPanel.tsx  # HITL approve/reject with rationale
│       └── pages/
│           ├── Dashboard.tsx    # Use case list + template creation
│           └── Editor.tsx       # Composition layer for all editor components
├── templates/                   # Blueprint template files
├── docker-compose.yml
├── Dockerfile                   # Multi-stage (frontend build + Python runtime)
├── requirements.txt
└── run.py                       # Entry point
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/usecases` | GET/POST | List/Create use cases |
| `/api/usecases/:id` | GET/PUT/DELETE | Get/Update/Delete use case |
| `/api/usecases/:id/workflow` | POST/GET | Create/Get workflow for use case |
| `/api/usecases/:id/workflow/progress` | GET | Workflow step progress summary |
| `/api/usecases/:id/workflow/steps/:step/execute` | POST | Execute a workflow step |
| `/api/usecases/:id/workflow/steps/:step/review` | POST | Submit HITL review (approve/reject) |
| `/api/usecases/:id/state/transition` | POST | IRM state machine transition |
| `/api/upload` | POST | Upload + extract document |
| `/api/hopex/capabilities` | GET | List HOPEX capabilities |
| `/api/hopex/search` | GET | Search HOPEX elements |
| `/api/export/markdown/:id` | GET | Export as Markdown |
| `/api/export/word/:id` | GET | Export as Word |
| `/api/export/irm/:id` | GET | Export as IRM JSON-LD |

## Environment

See `.env.example` for all configuration options. Only `DATABASE_URL` matters for basic operation — everything else is optional with graceful fallbacks.

## License

MIT
