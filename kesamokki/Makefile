include custom.mk

setup-env:
	@echo ".env file already exists or is being used."

start: ## Start the docker containers
	@echo "Starting the docker containers"
	@docker compose -f docker-compose.local.yml up

stop: ## Stop Containers
	@docker compose -f docker-compose.local.yml down

restart: stop start ## Restart Containers

start-bg:  ## Run containers in the background
	@docker compose -f docker-compose.local.yml up -d

build: ## Build Containers
	@docker compose -f docker-compose.local.yml build

ssh: ## SSH into running django container
	docker compose exec django bash

bash: ## Get a bash shell into the django container
	docker compose run --rm --no-deps django bash

manage: ## Run any manage.py command. E.g. `make manage ARGS='createsuperuser'`
	@docker compose -f docker-compose.local.yml run --rm django python manage.py ${ARGS}

migrations: ## Create DB migrations in the container
	@docker compose run --rm django python manage.py makemigrations

migrate: ## Run DB migrations in the container
	@docker compose run --rm django python manage.py migrate

translations:
	@docker compose run --rm --no-deps django python manage.py makemessages --all --ignore node_modules --ignore venv --ignore .venv
	@docker compose run --rm --no-deps django python manage.py makemessages -d djangojs --all --ignore node_modules --ignore venv --ignore .venv
	@docker compose run --rm --no-deps django python manage.py compilemessages --ignore venv --ignore .venv

shell: ## Get a Django shell
	@docker compose run --rm django python manage.py shell

dbshell: ## Get a Database shell
	@docker compose exec postgres psql -U postgres kesamokki

test: ## Run Django tests
	@docker compose run --rm django python manage.py test ${ARGS}

init: setup-env start-bg migrations migrate  ## Quickly get up and running (start containers and migrate DB)

pip_compile_cmd = uv pip compile --no-emit-package setuptools --no-strip-extras
pip-compile: ## Compiles your requirements.in file to requirements.txt
	@docker compose run --rm --no-deps django $(pip_compile_cmd) requirements/requirements.in -o requirements/requirements.txt
	@docker compose run --rm --no-deps django $(pip_compile_cmd) requirements/dev-requirements.in -o requirements/dev-requirements.txt
	@docker compose run --rm --no-deps django $(pip_compile_cmd) requirements/prod-requirements.in -o requirements/prod-requirements.txt

requirements: pip-compile build stop start-bg  ## Rebuild your requirements and restart your containers

ruff-format: ## Runs ruff formatter on the codebase
	@docker compose run --rm --no-deps django ruff format .

ruff-lint:  ## Runs ruff linter on the codebase
	@docker compose run --rm --no-deps django ruff check --fix  .

format: ruff-format ruff-lint ## Formatting and linting using Ruff

npm-install: ## Runs npm install in the container
	@docker compose run --rm --no-deps node npm install $(filter-out $@,$(MAKECMDGOALS))

npm-uninstall: ## Runs npm uninstall in the container
	@docker compose run --rm --no-deps node npm uninstall $(filter-out $@,$(MAKECMDGOALS))

npm-build: ## Runs npm build in the container (for production assets)
	@docker compose run --rm --no-deps node npm run build

npm-dev: ## Runs npm dev in the container
	@docker compose run --rm --no-deps node npm run dev

npm-watch: ## Runs npm watch in the container (recommended for dev)
	@docker compose run --rm --no-deps node npm run dev-watch

npm-type-check: ## Runs the type checker on the front end TypeScript code
	@docker compose run --rm --no-deps node npm run type-check

build-api-client:  ## Update the JavaScript API client code.
	@docker run --rm --network host -v $(shell pwd)/api-client:/local openapitools/openapi-generator-cli:v7.9.0 generate \
	-i http://localhost:8000/api/schema/ \
	-g typescript-fetch \
	-o /local/

upgrade: requirements migrations migrate npm-install npm-dev

gcp-build:  ## Build your docker container for Google Cloud
	@docker build -t ${IMAGE_URL} . -f Dockerfile.web --platform linux/amd64

gcp-push:  ## Push your docker container for Google Cloud
	@docker push ${IMAGE_URL}

gcp-deploy:  ## Deploy the latest docker container to Google Cloud
	@gcloud run deploy kesamokki-app-web \
	--region ${REGION} \
	--update-env-vars DJANGO_SETTINGS_MODULE=kesamokki.settings_production \
	--image ${IMAGE_URL} \
	--set-cloudsql-instances ${DATABASE_ADDRESS} \
	--network ${REDIS_NETWORK} \
	--set-secrets APPLICATION_SETTINGS=application_settings:latest \
	--service-account ${SERVICE_ACCOUNT} \
	--allow-unauthenticated

gcp-full-deploy: gcp-build gcp-push gcp-deploy  ## Build, push, and deploy the latest code to Google Cloud

gcp-sql-shell:  ## Get a Google Cloud SQL shell
	gcloud sql connect ${DATABASE_INSTANCE_NAME} --user=${DATABASE_USER} --database=${DATABASE_NAME}

.PHONY: help
.DEFAULT_GOAL := help

help:
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# catch-all for any undefined targets - this prevents error messages
# when running things like make npm-install <package>
%:
	@: