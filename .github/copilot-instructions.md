# Xiaole AI Copilot Instructions

## 🏗 Project Architecture

- **Type**: Personal AI Assistant (Python Backend + Vue 3 Frontend).
- **Backend**: FastAPI (`backend/main.py`), SQLAlchemy, PostgreSQL (NAS).
- **Frontend**: Vue 3, Vite, Pinia, Vue Router (`frontend/`).
- **Core Logic**: `backend/agent.py` orchestrates tools, memory, and conversation.
- **Tools**: Standalone modules in `tools/` (e.g., `weather_tool.py`), registered in `agent.py`.
- **Data**: PostgreSQL on Synology NAS. Migrations are raw SQL in `backend/db_migrations/`.

## 🚀 Development Workflow

- **Start Services**: Use `./start.sh` (starts backend & frontend).
- **Stop Services**: Use `./stop.sh`.
- **Backend Dev**: `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
- **Frontend Dev**: `cd frontend && npm run dev`.
- **Git Commit**: ALWAYS use `./scripts/auto_commit.sh` for interactive, standardized commits.
- **Migrations**: SQL files in `backend/db_migrations/`. Run via `python scripts/run_migration.py`.

## 🐍 Backend Patterns (Python/FastAPI)

- **Imports**: `backend/agent.py` modifies `sys.path` to import from `tools/`. Respect this pattern.
- **Tool Registration**: To add a tool:
  1. Create `tools/your_tool.py`.
  2. Import and register it in `backend/agent.py` inside `_register_tools`.
- **Configuration**: Use `os.getenv` with defaults. Configs are in `.env`.
- **Async**: `agent.py` uses `asyncio` for tool execution. Ensure tools are compatible.
- **Static Files**: `backend/static` is mounted. `backend/uploads` stores user content.

## ⚡️ Frontend Patterns (Vue 3)

- **State Management**: Use Pinia (`frontend/src/stores`).
- **Routing**: Vue Router (`frontend/src/router`).
- **Components**: Located in `frontend/src/components`. Views in `frontend/src/views`.
- **API Calls**: Use `fetch` or `axios` pointing to backend (default port 8000).

## 🧪 Testing & Debugging

- **Tests**: `tests/` directory. Run specific tests like `python tests/test_agent.py`.
- **Logs**: Check `logs/xiaole_ai.log` (backend) and browser console (frontend).
- **Scripts**: Use `scripts/` for maintenance (e.g., `fix_memory_data.py`, `debug_reminders.py`).

## ⚠️ Critical Conventions

- **Do NOT** hardcode API keys. Use `.env`.
- **Do NOT** modify `backend/db_migrations/` existing files. Create NEW numbered SQL files.
- **Pathing**: Use absolute paths or `os.path.join(BASE_DIR, ...)` in backend to avoid CWD issues.
