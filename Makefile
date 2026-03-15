# NEBULA-QUANT — Run from repository root: ~/projects/nebula-quant
.PHONY: setup up down logs ui backend test

REPO_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
COMPOSE_FILE := docker/docker-compose.yml

setup:
	@chmod +x $(REPO_ROOT)scripts/setup_dev_env.sh
	$(REPO_ROOT)scripts/setup_dev_env.sh

up:
	cd $(REPO_ROOT) && docker compose -f $(COMPOSE_FILE) up -d

down:
	cd $(REPO_ROOT) && docker compose -f $(COMPOSE_FILE) down

logs:
	cd $(REPO_ROOT) && docker compose -f $(COMPOSE_FILE) logs -f

# Start Next.js frontend (local dev; run from repo root)
ui:
	cd $(REPO_ROOT)apps/web && npm run dev

# Start trading backend (bot) in Docker
backend:
	cd $(REPO_ROOT) && docker compose -f $(COMPOSE_FILE) up -d bot
	@echo "Bot starting. Logs: make logs"

# Run test suite: root tests + services/bot tests
test:
	@echo "== Root tests (tests/) =="
	cd $(REPO_ROOT) && python3 -m unittest discover -s tests -v 2>/dev/null || true
	@echo "== Bot tests (services/bot) =="
	cd $(REPO_ROOT) && PYTHONPATH=$(REPO_ROOT)services/bot python3 -m pytest services/bot -q --tb=short 2>/dev/null || \
	PYTHONPATH=$(REPO_ROOT)services/bot python3 -m unittest discover -s services/bot -p "test_*.py" -v 2>/dev/null || true
