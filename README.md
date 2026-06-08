# Generative Agents Course Demo

This repository contains a course-demo-scale reproduction of *Generative Agents: Interactive Simulacra of Human Behavior*.

## For Reviewers

If you only want to pull the code and run the demo locally:

```bash
git clone https://github.com/guojiageng99/three.git
cd three
```

Then:

1. Start the backend on `127.0.0.1:8000`
2. Start the frontend on `localhost:3000`
3. Open `http://localhost:3000`
4. Advance the simulation from the UI and observe movement, memory, dialogue, and reflection

## Project Scope

The system focuses on a minimum complete cognitive loop for classroom demonstration:

- a small town map with 4 locations
- 3 NPCs: Alice, Bob, and Carol
- time progression and schedule-driven movement
- memory recording and lightweight retrieval
- action and dialogue generation
- reflection generation after social information spreads
- a frontend panel that explains plans, retrieved memories, and reasoning

## Demo Storyline

The built-in storyline is stable for recording and presentation:

- `10:00` Alice shares the evening gathering with Bob
- `14:00` Bob passes the information to Carol
- after 3 agents know the event, the system produces shared reflection

This makes the demo easy to explain and repeat during a 10-minute course presentation.

## What To Look At In The Demo

When reviewing the project, focus on these behaviors:

- agents move between locations according to schedule
- each agent keeps its own memory stream
- later actions and dialogue depend on recalled memories
- information spreads from one agent to another over time
- once enough social information accumulates, the system generates reflection

This is a teaching demo, so the goal is not a giant open-world simulation. The goal is to show the core cognitive loop of generative agents in a small, repeatable scenario.

## Tech Stack

- Frontend: Next.js + React
- Backend: FastAPI + Python
- Model mode: OpenAI-compatible API or deterministic fallback

## Run

Python `3.10+` is required. The current local setup was verified with Python `3.12.4`.
If you previously created `backend/.venv` with Python `3.9`, delete that virtual environment and recreate it before installing dependencies.

## Quick Start

If you want the shortest path:

1. Prepare Python `3.10+` and Node.js
2. Install backend dependencies from `backend/requirements.txt`
3. Install frontend dependencies from `frontend/package.json`
4. Start backend on port `8000`
5. Set `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`
6. Start frontend and open `http://localhost:3000`

### Recommended Conda Setup

The local machine has already been prepared with a dedicated conda environment:

```bash
conda activate ga-demo
```

If you ever need to recreate it:

```bash
conda create -n ga-demo python=3.12 -y
conda run -n ga-demo python -m pip install -r backend/requirements.txt
```

### Backend

Recommended on Windows `cmd`:

```bat
conda activate ga-demo
cd /d E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Recommended on Windows PowerShell:

```powershell
conda activate ga-demo
cd E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If you prefer a local virtual environment instead of conda:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

Windows `cmd`:

```bat
cd /d E:\demo\buaa\suanfa\three\frontend
set NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
npm install
npm run dev
```

Windows PowerShell:

```powershell
cd E:\demo\buaa\suanfa\three\frontend
$env:NEXT_PUBLIC_API_BASE="http://127.0.0.1:8000"
npm install
npm run dev
```

Open `http://localhost:3000` after both services start.

## Suggested Review Flow

For a teammate or reviewer, this order is the easiest:

1. Read this `README.md`
2. Run backend and frontend locally
3. Open the page and step through the built-in story
4. Check `submission_docs/` for PPT, scripts, and report materials
5. If needed, inspect `backend/app/` and `frontend/` for implementation details

## Optional LLM Mode

The backend supports an OpenAI-compatible chat API.

```bash
set LLM_API_KEY=your_key
set LLM_BASE_URL=https://api.openai.com/v1
set LLM_MODEL=gpt-4o-mini
```

If `LLM_API_KEY` is not set, the simulation still runs with deterministic fallback behavior for plans, actions, dialogue, and reflections.

## Submission Materials

Prepared course materials are under `submission_docs/`:

- PPT deck
- report drafts and final markdown versions
- per-slide script
- 10-minute video script
- screenshots for the reports and slides

## Short Explanation For Teammates

You can forward this summary directly:

> This project is a small classroom demo of Generative Agents. The frontend visualizes a town map and each agent's plan, memory, reasoning, and dialogue. The backend simulates schedule, memory retrieval, dialogue generation, and reflection. By default it can run without an API key using deterministic fallback logic, so it is easy to reproduce locally.
