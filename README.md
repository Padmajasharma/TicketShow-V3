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
