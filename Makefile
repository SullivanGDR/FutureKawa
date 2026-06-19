SHELL := bash
.PHONY: start stop clean logs restart test test-backend test-frontend help

start:
	docker compose up --build -d
	@echo ""
	@echo "==> FutureKawa demarré"
	@echo "    Frontend  : http://localhost:3000"
	@echo "    Backend   : http://localhost:8000"
	@echo "    API docs  : http://localhost:8000/docs"
	@echo "    pgAdmin   : http://localhost:5050  (admin@futurekawa.com / admin)"
	@echo "    Jenkins   : http://localhost:8080  (admin / admin) — pipeline: FutureKawa-Pipeline"
	@echo "    MQTT      : localhost:1883"

stop:
	docker compose down

clean:
	docker compose down -v --remove-orphans

logs:
	docker compose logs -f

restart: stop start

test: test-backend test-frontend

test-backend:
	@echo "==> Tests Backend (pytest)"
	docker compose build backend
	mkdir -p FutureKawaBresil_API/test-results
	docker run --rm \
		-e DATABASE_URL=postgresql+asyncpg://unused:unused@localhost/test \
		futurekawa-backend:latest \
		sh -c "pip install --quiet pytest && pytest tests/ -v --tb=short"

test-frontend:
	@echo "==> Tests Frontend (vitest)"
	docker compose build frontend
	docker run --rm \
		futurekawa-frontend:latest \
		sh -c "npm run test"

help:
	@echo "Commandes disponibles:"
	@echo "  make start          — Commit git + Build + lancement de tous les services"
	@echo "  make stop           — Arret (volumes conserves)"
	@echo "  make clean          — Arret + suppression volumes (reset DB)"
	@echo "  make restart        — Redemarrage"
	@echo "  make logs           — Logs en temps reel"
	@echo "  make test           — Backend + Frontend tests (console)"
	@echo "  make test-backend   — Tests Python uniquement"
	@echo "  make test-frontend  — Tests TypeScript uniquement"
