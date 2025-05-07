.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker commands
.PHONY: build up down restart logs ps shell npm-install

build: ## Build docker containers
	docker-compose -f docker-compose.local.yml build

up: ## Start docker containers
	docker-compose -f docker-compose.local.yml up

up-d: ## Start docker containers in detached mode
	docker-compose -f docker-compose.local.yml up -d

down: ## Stop docker containers
	docker-compose -f docker-compose.local.yml down

restart: ## Restart docker containers
	docker-compose -f docker-compose.local.yml restart

logs: ## Show logs from all containers
	docker-compose -f docker-compose.local.yml logs

logs-f: ## Show and follow logs from all containers
	docker-compose -f docker-compose.local.yml logs -f

ps: ## Show running containers
	docker-compose -f docker-compose.local.yml ps

shell: ## Open a Django shell
	docker-compose -f docker-compose.local.yml run --rm django python manage.py shell

bash: ## Open a bash shell in the Django container
	docker-compose -f docker-compose.local.yml run --rm django bash
manage: ## Run a Django management command
	docker-compose -f docker-compose.local.yml run --rm django python manage.py $(command)
	@echo "Usage: make manage command=<your_command>"

# Django commands
.PHONY: makemigrations migrate collectstatic createsuperuser test coverage

makemigrations: ## Create database migrations
	docker-compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

migrate: ## Apply database migrations
	docker-compose -f docker-compose.local.yml run --rm django python manage.py migrate

collectstatic: ## Collect static files
	docker-compose -f docker-compose.local.yml run --rm django python manage.py collectstatic --no-input

createsuperuser: ## Create a superuser
	docker-compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

test: ## Run tests
	docker-compose -f docker-compose.local.yml run --rm django python manage.py test

test-app: ## Run tests for a specific app (usage: make test-app app=reservations)
	@if [ -z "$(app)" ]; then \
		echo "Please specify an app name. Example: make test-app app=reservations"; \
	else \
		docker-compose -f docker-compose.local.yml run --rm django python manage.py test $(app); \
	fi

coverage: ## Run tests with coverage
	docker-compose -f docker-compose.local.yml run --rm django coverage run -m pytest
	docker-compose -f docker-compose.local.yml run --rm django coverage report

# Frontend commands
.PHONY: npm-install npm-dev npm-build

npm-install: ## Install npm dependencies
	docker-compose -f docker-compose.local.yml run --rm node npm install

npm-dev: ## Run npm dev server
	docker-compose -f docker-compose.local.yml run --rm node npm run dev

npm-build: ## Build frontend assets
	docker-compose -f docker-compose.local.yml run --rm node npm run build

# Production commands
.PHONY: prod-build prod-up prod-down

prod-build: ## Build production docker containers
	docker-compose -f docker-compose.production.yml build

prod-up: ## Start production docker containers
	docker-compose -f docker-compose.production.yml up -d

prod-down: ## Stop production docker containers
	docker-compose -f docker-compose.production.yml down

# Documentation commands
.PHONY: docs-build docs-serve

docs-build: ## Build documentation
	docker-compose -f docker-compose.docs.yml run --rm docs make html

docs-serve: ## Serve documentation
	docker-compose -f docker-compose.docs.yml up

# Utility commands
.PHONY: clean

clean: ## Remove all build, test, coverage and Python artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr htmlcov/
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
	find . -name '__pycache__' -delete

# Multiple commands
.PHONY: setup restart-and-migrate rebuild

setup: down build up-d migrate npm-install npm-build collectstatic ## Setup project (build, start, migrate, install npm, collect static)

restart-and-migrate: down up-d migrate ## Restart containers and run migrations

rebuild: down build up-d ## Rebuild and restart containers

# Daily development commands
.PHONY: start dev-start

start: ## Quick start for day-to-day development (no rebuilding)
	@echo "Stopping any existing containers..."
	@make down
	@echo "Starting containers in detached mode..."
	@make up-d
	@echo "Project is now running! Visit http://localhost:8000"

dev-start: down up-d npm-build collectstatic ## Start with frontend asset rebuilding
	@echo "Project is now running with rebuilt assets! Visit http://localhost:8000"

full-setup: down build up-d migrate npm-install npm-build collectstatic ## Complete setup from scratch
	@echo "Full project setup complete! Visit http://localhost:8000"