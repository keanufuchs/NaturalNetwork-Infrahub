# Makefile for infrahub-aci project

# Variables
INFRAHUB_IMAGE_VER ?=
INFRAHUB_COMPOSE_URL ?= https://infrahub.opsmill.io
COMPOSE_FILE = docker-compose.yml
PYTHON_VERSION = 3.13

# Get current git branch
BRANCH_NAME := $(shell git branch --show-current)


# Cleanup the Branch
cleanup:
	@echo "Cleaning up InfraHub branch: $(BRANCH_NAME)..."
	make delete-branch
	make create-branch
	make load-schema
	make load-menu
	make load-objects

# Safety check - fail if on main branch
check-branch:
	@if [ "$(BRANCH_NAME)" = "NOmain" ]; then \
		echo "Error: This command cannot be run on the main branch. Please switch to a development branch."; \
		exit 1; \
	fi

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# InfraHub CLI targets
.PHONY: create-branch
create-branch: ## Create a new InfraHub branch (use BRANCH_NAME=branch_name)
	@if [ -z "$(BRANCH_NAME)" ]; then \
		echo "Error: BRANCH_NAME is required. Usage: make create-branch BRANCH_NAME=my-branch"; \
		exit 1; \
	fi
	@if [ "$(BRANCH_NAME)" = "main" ]; then \
		echo "Error: Cannot create branch named 'main'. Please choose a different branch name."; \
		exit 1; \
	fi
	@echo "Creating InfraHub branch: $(BRANCH_NAME)..."
	uv run infrahubctl branch create --sync-with-git $(BRANCH_NAME)

.PHONY: delete-branch
delete-branch: check-branch ## Delete a new InfraHub branch (use BRANCH_NAME=branch_name)
	@if [ "$(BRANCH_NAME)" = "main" ]; then \
		echo "Error: Cannot delete branch named 'main'. Please choose a different branch name."; \
		exit 1; \
	fi
	@echo "Deleting InfraHub branch: $(BRANCH_NAME)..."
	uv run infrahubctl branch delete $(BRANCH_NAME) || true

.PHONY: load-menu
load-menu: ## Load schemas into InfraHub using infrahubctl
	@echo "Loading menu schemas..."
	uv run infrahubctl menu load --branch $(BRANCH_NAME) menus/ || true

.PHONY: load-objects
load-objects: check-branch ## Load objects into InfraHub using infrahubctl
	@echo "Loading objects..."
	uv run infrahubctl object load --branch $(BRANCH_NAME) objects || true

.PHONY: load-schema
load-schema: check-branch ## Load schema into InfraHub using infrahubctl
	@echo "Loading schema..."
	uv run infrahubctl schema load --branch ${BRANCH_NAME} schemas/

.PHONY: reset-branch
reset-branch: check-branch delete-branch create-branch load-schema load-menu load-objects
	@echo "Resetting branch: $(BRANCH_NAME)..."

# Testing targets
.PHONY: test
test: ## Run tests using pytest
	@echo "Running tests..."
	uv run pytest tests

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "Running tests with verbose output..."
	uv run pytest tests -v

# Code formatting and linting targets
.PHONY: format
format: ## Run ruff to format all Python files
	@echo "Formatting Python files..."
	uv run ruff format .
	uv run ruff check . --fix

.PHONY: lint-yaml
lint-yaml: ## Run yamllint to check all YAML files
	@echo "Checking YAML files with yamllint..."
	uv run yamllint .

.PHONY: lint-mypy
lint-mypy: ## Run mypy to check type annotations
	@echo "Checking type annotations with mypy..."
	uv run mypy src/

.PHONY: lint-ruff
lint-ruff: ## Run ruff to check Python code
	@echo "Checking Python code with ruff..."
	uv run ruff check .

.PHONY: lint
lint: lint-yaml lint-ruff lint-mypy ## Run all linters

.PHONY: lint-fix
lint-fix: ## Run linters with auto-fix where possible
	@echo "Running linters with auto-fix..."
	uv run ruff check . --fix
	uv run ruff format .

# Development setup targets
.PHONY: install
install: ## Install dependencies using uv
	@echo "Installing dependencies..."
	uv sync

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	uv sync --dev

.PHONY: clean
clean: ## Clean up temporary files and caches
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	rm -rf build/ dist/ *.egg-info/

.PHONY: clean-docker
clean-docker: ## Clean up Docker containers and images
	@echo "Cleaning up Docker resources..."
	docker compose down -v --remove-orphans
	docker system prune -f

# Load environment variables from .env file
ifneq ($(wildcard .env),)
$(foreach line,$(shell grep -v '^#' .env | grep -v '^$$'),$(eval export $(line)))
endif

# Load environment variables
.PHONY: load-env
load-env: ## Load environment variables from .env file
	@if [ -f .env ]; then \
		echo "Loading environment variables from .env..."; \
		echo "Environment variables loaded successfully!"; \
		echo "Available variables:"; \
		grep -v '^#' .env | grep -v '^$$' | cut -d'=' -f1 | sed 's/^/  - /'; \
	else \
		echo "Warning: .env file not found. Create one with your environment variables."; \
		echo "Example .env file:"; \
		echo "  INFRAHUB_IMAGE_VER=latest"; \
		echo "  INFRAHUB_COMPOSE_URL=https://infrahub.opsmill.io"; \
	fi

.PHONY: env-export
env-export: ## Export environment variables for shell sourcing
	@if [ -f .env ]; then \
		echo "export"; \
		grep -v '^#' .env | grep -v '^$$' | sed 's/^/export /'; \
	else \
		echo "echo 'Error: .env file not found'"; \
	fi

# Application targets
.PHONY: run
run: ## Run the infrahub-aci application
	@echo "Running infrahub-aci..."
	uv run infrahub-aci

.PHONY: run-module
run-module: ## Run the application as a Python module
	@echo "Running infrahub-aci as module..."
	uv run python -m infrahub_aci.main

# CI/CD targets
.PHONY: ci-lint
ci-lint: ## Run linting as it would run in CI
	@echo "Running CI linting checks..."
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/
	uv run yamllint .gitlab-ci.yml .yamllint.yml

.PHONY: ci-test
ci-test: ## Run tests as they would run in CI
	@echo "Running CI tests..."
	uv run pytest tests --cov=src/infrahub_aci --cov-report=xml

# Documentation targets
.PHONY: docs
docs: ## Generate documentation (placeholder for future Sphinx setup)
	@echo "Documentation generation not yet implemented"

# Security targets
.PHONY: security-check
security-check: ## Run security checks (placeholder for future bandit setup)
	@echo "Security checks not yet implemented"

# All-in-one targets
.PHONY: setup
setup: install-dev ## Set up the development environment
	@echo "Development environment setup complete!"

.PHONY: check
check: lint test ## Run all checks (linting and tests)

.PHONY: pre-commit
pre-commit: format lint test ## Run pre-commit checks
	@echo "Pre-commit checks completed successfully!"

# Docker development targets
.PHONY: dev-start
dev-start: start load-objects ## Start development environment with objects loaded
	@echo "Development environment started with objects loaded"

.PHONY: dev-stop
dev-stop: stop ## Stop development environment
	@echo "Development environment stopped"

.PHONY: dev-restart
dev-restart: restart load-objects ## Restart development environment with objects loaded
	@echo "Development environment restarted with objects loaded"

# Service Catalog targets
.PHONY: service-catalog-start
service-catalog-start: ## Start the service catalog application
	@echo "Starting service catalog..."
	cd service-catalog && docker compose up -d
	@echo "Service catalog started."
	@echo "  - Application: http://localhost"
	@echo "  - Traefik Dashboard: http://localhost:8081"

.PHONY: service-catalog-stop
service-catalog-stop: ## Stop the service catalog application
	@echo "Stopping service catalog..."
	cd service-catalog && docker compose down
	@echo "Service catalog stopped"

.PHONY: service-catalog-restart
service-catalog-restart: ## Restart the service catalog application
	@echo "Restarting service catalog..."
	cd service-catalog && docker compose restart
	@echo "Service catalog restarted"

.PHONY: service-catalog-logs
service-catalog-logs: ## View service catalog logs
	@echo "Viewing service catalog logs..."
	cd service-catalog && docker compose logs -f

.PHONY: service-catalog-build
service-catalog-build: ## Build the service catalog Docker image
	@echo "Building service catalog image..."
	cd service-catalog && docker compose build
	@echo "Service catalog image built"

.PHONY: service-catalog-rebuild
service-catalog-rebuild: ## Stop, rebuild and start the service catalog application
	@echo "Stopping service catalog..."
	cd service-catalog && docker compose down
	@echo "Building service catalog image (using BuildKit cache for faster rebuilds)..."
	@DOCKER_BUILDKIT=1 cd service-catalog && docker compose build
	@echo "Starting service catalog..."
	cd service-catalog && docker compose up -d
	@echo "Service catalog restarted"
	@echo "  - Application: http://localhost"
	@echo "  - Traefik Dashboard: http://localhost:8081"
