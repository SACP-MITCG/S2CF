# S2CF — Sustainable Supply Chain Framework

S2CF is a toolkit for designing and documenting solution architectures in sustainable supply chain contexts. It combines AI-assisted business analysis with architecture co-creation, built around enterprise standards (IRM, TOGAF) and integration with tools like MEGA HOPEX.

## Components

| Component | What it does | Status |
|-----------|-------------|--------|
| **[BAC](bac/)** — Business Analysis Copilot | Create and manage business use case descriptions with embedded architecture references | Active development |
| **[SAC](sac/)** — Solution Architecture Copilot | Generate solution architecture and deployable artifacts from BAC output | Scaffold |

BAC is the upstream tool — its output (IRM JSON-LD) feeds into SAC.

## Quick Start

```bash
cp .env.example .env
docker-compose up --build
```

This starts BAC, SAC, PostgreSQL, and Redis. BAC is available at **http://localhost:5001**.

See [bac/README.md](bac/README.md) for detailed setup options (local dev, frontend-only).

## Project Board

Active work is tracked on the [BAC Project Board](https://github.com/orgs/SACP-MITCG/projects/9).
