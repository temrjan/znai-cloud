.PHONY: help setup install-deps run test clean backup

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help: ## Show this help message
	@echo "$(GREEN)AI-Avangard - Available Commands:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ==============================================================================
# INSTALLATION
# ==============================================================================

setup: ## Install all system dependencies (requires sudo)
	@echo "$(GREEN)Installing system dependencies...$(RESET)"
	sudo ./infrastructure/scripts/setup.sh

install-deps: ## Install Python and Node dependencies
	@echo "$(GREEN)Installing backend dependencies...$(RESET)"
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r backend/requirements.txt
	./venv/bin/pip install -r backend/requirements-dev.txt
	@echo "$(GREEN)Installing frontend dependencies...$(RESET)"
	cd frontend && npm install

# ==============================================================================
# DEVELOPMENT
# ==============================================================================

run-backend: ## Run backend development server
	./venv/bin/uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run frontend development server
	cd frontend && npm run dev

run: ## Run both backend and frontend (in parallel)
	@echo "$(GREEN)Starting backend and frontend...$(RESET)"
	@make -j2 run-backend run-frontend

# ==============================================================================
# TESTING
# ==============================================================================

test-backend: ## Run backend tests
	./venv/bin/pytest backend/tests/ -v --cov=backend/app

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: ## Run all tests
	@make test-backend
	@make test-frontend

test-watch: ## Run tests in watch mode
	cd frontend && npm test -- --watch

# ==============================================================================
# CODE QUALITY
# ==============================================================================

lint-backend: ## Lint backend code
	./venv/bin/black backend/app backend/tests
	./venv/bin/isort backend/app backend/tests
	./venv/bin/flake8 backend/app backend/tests
	./venv/bin/mypy backend/app

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint
	cd frontend && npm run format

lint: ## Lint all code
	@make lint-backend
	@make lint-frontend

# ==============================================================================
# DATABASE
# ==============================================================================

db-migrate: ## Run database migrations
	./venv/bin/alembic upgrade head

db-migrate-create: ## Create new migration
	@read -p "Enter migration message: " msg; \
	./venv/bin/alembic revision --autogenerate -m "$$msg"

db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(YELLOW)WARNING: This will destroy all data!$(RESET)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		sudo -u postgres psql -c "DROP DATABASE IF EXISTS ai_avangard;"; \
		sudo -u postgres psql -c "CREATE DATABASE ai_avangard;"; \
		sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_avangard TO ai_avangard_admin;"; \
		make db-migrate; \
		echo "$(GREEN)Database reset complete$(RESET)"; \
	else \
		echo "Cancelled"; \
	fi

# ==============================================================================
# SERVICES
# ==============================================================================

services-status: ## Check status of all services
	@echo "$(GREEN)Checking services...$(RESET)"
	@systemctl is-active postgresql && echo "✓ PostgreSQL: running" || echo "✗ PostgreSQL: stopped"
	@systemctl is-active redis-server && echo "✓ Redis: running" || echo "✗ Redis: stopped"
	@systemctl is-active qdrant && echo "✓ Qdrant: running" || echo "✗ Qdrant: stopped"

services-restart: ## Restart all services
	sudo systemctl restart postgresql
	sudo systemctl restart redis-server
	sudo systemctl restart qdrant

logs-backend: ## Show backend logs
	tail -f logs/backend.log

logs-qdrant: ## Show Qdrant logs
	sudo journalctl -u qdrant -f

logs-postgres: ## Show PostgreSQL logs
	sudo journalctl -u postgresql -f

# ==============================================================================
# BUILD
# ==============================================================================

build-frontend: ## Build frontend for production
	cd frontend && npm run build

build: build-frontend ## Build all for production

# ==============================================================================
# DEPLOYMENT
# ==============================================================================

deploy-setup-nginx: ## Setup Nginx configuration
	sudo cp infrastructure/nginx/ai-avangard.conf /etc/nginx/sites-available/
	sudo ln -sf /etc/nginx/sites-available/ai-avangard.conf /etc/nginx/sites-enabled/
	sudo nginx -t
	sudo systemctl reload nginx

deploy-setup-systemd: ## Setup systemd service for backend
	sudo cp infrastructure/systemd/ai-avangard-backend.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable ai-avangard-backend

deploy: build deploy-setup-nginx deploy-setup-systemd ## Deploy to production
	sudo systemctl restart ai-avangard-backend
	@echo "$(GREEN)Deployment complete!$(RESET)"

# ==============================================================================
# MAINTENANCE
# ==============================================================================

clean: ## Clean build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/dist frontend/.vite frontend/node_modules/.vite
	rm -rf .pytest_cache .coverage htmlcov

backup: ## Backup database and user data
	@echo "$(GREEN)Creating backup...$(RESET)"
	mkdir -p backups
	sudo -u postgres pg_dump ai_avangard | gzip > backups/ai_avangard_$$(date +%Y%m%d_%H%M%S).sql.gz
	tar -czf backups/user_data_$$(date +%Y%m%d_%H%M%S).tar.gz data/users/
	@echo "$(GREEN)Backup complete!$(RESET)"

health-check: ## Check system health
	@echo "$(GREEN)System Health Check:$(RESET)"
	@echo ""
	@echo "Services:"
	@make services-status
	@echo ""
	@echo "API:"
	@curl -s http://localhost:8000/health | jq || echo "Backend not running"
	@echo ""
	@echo "Qdrant:"
	@curl -s http://localhost:6333/health | jq || echo "Qdrant not running"

# ==============================================================================
# DOCUMENTATION
# ==============================================================================

docs: ## Open documentation
	@echo "Opening documentation..."
	@echo "README.md: $(PWD)/README.md"
	@echo "ARCHITECTURE.md: $(PWD)/docs/ARCHITECTURE.md"

# ==============================================================================
# QUICK SETUP (for first-time users)
# ==============================================================================

first-time-setup: ## Complete first-time setup
	@echo "$(GREEN)Starting first-time setup...$(RESET)"
	@make setup
	@make install-deps
	@if [ ! -f .env ]; then cp .env.example .env; echo "$(YELLOW)Created .env file - please edit with your API keys$(RESET)"; fi
	@make db-migrate
	@echo "$(GREEN)First-time setup complete!$(RESET)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Edit .env file with your OpenAI API key"
	@echo "  2. Run: make run"
	@echo "  3. Open http://localhost:5173"
