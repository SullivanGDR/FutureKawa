SHELL := bash
.PHONY: start stop clean logs restart test help

start:
	docker compose up --build -d
	@echo ""
	@echo "==> FutureKawa demarré"
	@echo "    Frontend  : http://localhost:3000"
	@echo "    Backend   : http://localhost:8000"
	@echo "    API docs  : http://localhost:8000/docs"
	@echo "    pgAdmin   : http://localhost:5050  (admin@futurekawa.com / admin)"
	@echo "    MQTT      : localhost:1883"

stop:
	docker compose down

clean:
	docker compose down -v --remove-orphans

logs:
	docker compose logs -f

restart: stop start

# Tests unitaires (ne nécessitent pas de DB active)
test:
	docker compose build backend
	docker run --rm \
		-e DATABASE_URL=postgresql+asyncpg://unused:unused@localhost/test \
		futurekawa-backend:latest \
		sh -c "pip install --quiet pytest && pytest tests/ -v --tb=short"

help:
	@echo "Commandes disponibles:"
	@echo "  make start    — Build + lancement de tous les services"
	@echo "  make stop     — Arret des services (volumes conservés)"
	@echo "  make clean    — Arret + suppression volumes (reset DB)"
	@echo "  make restart  — Redémarrage"
	@echo "  make logs     — Logs en temps réel"
	@echo "  make test     — Tests unitaires via Docker"
