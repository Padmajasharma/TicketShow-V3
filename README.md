# TicketShow V3

This repository contains the TicketShow web application (Frontend + Backend). This README explains how to run the app locally for development.

## Contents
- `Backend/` — Flask backend, REST resources, Celery tasks and DB models
- `src/` — Vue 3 frontend

## Live Demo

Visit the deployed live demo at: https://ticket-show-v3.vercel.app/


## Prerequisites
- macOS / Linux / Windows with WSL
- Python 3.10+ (3.11 recommended)
- Node.js 16+ and `npm`
- Redis (for cache and Celery broker/result backends)
- (optional) MailHog or any SMTP server for development email testing
- Git and (optionally) `gh` CLI if you want to manage GitHub from the command line

If you don't have these installed, use Homebrew on macOS:

```bash
# Homebrew examples (macOS)
brew install python node redis mailhog
npm install -g @vue/cli # optional for Vue CLI tooling
```

## Quickstart — Backend (development)

1. Create a Python virtual environment and install dependencies

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Start Redis (if not already running)

```bash
# default redis server on localhost:6379
redis-server &
```

3. (Optional) Start MailHog to capture development emails

```bash
# If installed via Homebrew
mailhog &
# MailHog web UI: http://localhost:8025
```

4. Database migrations

The project includes Alembic migrations under `Backend/migrations`. Use Flask-Migrate via the Flask CLI.

```bash
cd Backend
# Set FLASK_APP to the run script
export FLASK_APP=run.py
# If migrations will run against a DB schema that expects Redis cache init
# avoid initializing the Redis cache during migrations
export SKIP_CACHE_INIT=1
flask db upgrade
unset SKIP_CACHE_INIT
```

If you are experimenting locally and prefer a quick dev DB, you can also initialize tables directly (not recommended for production):

```bash
python run.py # first run will create DB if missing depending on code paths, or use flask shell to run db.create_all()
```

5. Start the backend server

From the `Backend/` folder, run:

```bash
# start backend (binds to 0.0.0.0:5001)
python3 run.py
```

6. (Optional) Start a Celery worker for background tasks

```bash
# from project root (assumes `Backend/extensions.py` exposes celery)
cd Backend
source .venv/bin/activate
celery -A extensions.celery worker --loglevel=info
```

## Quickstart — Frontend (development)

1. Install dependencies and start dev server

```bash
cd ../ # project root
npm install
npm run serve

# Default dev server opens at http://localhost:8080
```

The frontend is configured to talk to the backend at `http://<host>:5001` (the app determines backend host from window.location). If you run the frontend on the same machine, requests will go to `http://localhost:5001` by default.

## Environment / Configuration

The backend reads configuration from `Backend/config.py` and environment variables. Important environment variables:

- `DATABASE_URL` / `SQLALCHEMY_DATABASE_URI` — (optional) override DB connection
- `SECRET_KEY` — Flask secret key (defaults are present in `config.py`, but you should set your own)
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` — Redis broker/result (defaults to `redis://localhost:6379/1` and `.../2`)
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` — SMTP settings for sending mail
- `SKIP_CACHE_INIT=1` — set during migrations to skip Redis initialization step

You can create a `.env` file in `Backend/` to set values for local development. The app uses `python-dotenv` to load it.

Example `.env` (do NOT commit this file):

```ini
SECRET_KEY=replace-with-a-secret
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USERNAME=
MAIL_PASSWORD=
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## Useful commands

- Seed sample shows into the DB:

```bash
cd Backend
export FLASK_APP=run.py
flask seed_shows
```

- Create an admin user:

```bash
cd Backend
export FLASK_APP=run.py
flask create_admin <username> <password>
```

- Inspect DB quickly (script examples may exist in `Backend/scripts/`)

## Running with Docker (optional)

If you prefer containers, there are Dockerfiles and a `docker-compose.prod.yml` in the repo. You will need to adapt them for development and provide secrets via environment variables.

## Troubleshooting

- If the frontend cannot reach the backend, ensure `python3 run.py` is running and that CORS is enabled (development config allows all origins).
- If you see Redis connection errors, verify `redis-server` is running and that `CACHE_REDIS_URL` / `CELERY_BROKER_URL` are correct.
- If Celery tasks are not being processed, make sure a Celery worker is running with the same config used by the app.

## Contributing

If you make changes, follow typical GitHub flow: create a branch, push, open a PR against `main` and add tests if possible.

## License

See `LICENSE` if present — add one if you plan to publish the project publicly (MIT is a good permissive choice).

---
If you want, I can: add a `README.md` directly to the repository (this file) — I will commit it for you now. Tell me if you want the README content edited (more deployment steps, screenshots, or CI instructions).
# TicketShow — Deployment & GitHub guide

This repository contains a Vue frontend and a Flask backend for a ticket booking app. Below are concise steps to put the project on GitHub and deploy it with Docker Compose (production example) or to a container platform.

1) Prepare local repo and push to GitHub
- create a new repository on GitHub (name: `ticketshow` or similar)
- locally:

```bash
cd /path/to/TicketShow\ V3
git init
git add .
git commit -m "Initial import"
git branch -M main
git remote add origin git@github.com:<your-username>/ticketshow.git
git push -u origin main
```

2) Build and run with Docker Compose (local/prod example)
- Ensure Docker and Docker Compose are installed.
- Copy `Backend/.env.example` to `Backend/.env` and fill secrets.

```bash
cp Backend/.env.example Backend/.env
# edit Backend/.env (secrets, DB password, mail config)
docker compose -f docker-compose.prod.yml up --build -d
```

3) Apply database migrations
- Exec into web container or run locally with your environment set, then run Alembic/Flask-Migrate upgrade:

```bash
docker compose exec web flask db upgrade
```

4) Start / scale workers

```bash
docker compose up -d --scale worker=2
```

5) Other deployment options
- Use Kubernetes: create Deployment + Service for `web`, a separate Deployment for `worker`, StatefulSet for Postgres, and a Redis Cluster or managed Redis.
- Use a managed container platform (ECS, Cloud Run, Azure Container Instances) and a managed Postgres + Redis.

6) Helpful production notes
- Use managed Redis and Postgres for HA and backups.
- Move static uploads/PDFs to S3 and serve through CDN.
- Add monitoring (Prometheus, Grafana), logging, tracing.

If you want, I can:
- create a GitHub Actions workflow that lints, tests, builds Docker images and optionally pushes to GitHub Container Registry.
- add S3 upload helpers for ticket PDFs and wire them into the app.
- create a minimal `k8s/` manifest for deploying to Kubernetes.

Tell me which next step you'd like me to implement. 
