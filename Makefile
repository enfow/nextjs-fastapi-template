# Root Makefile for Next.js FastAPI Template
.PHONY: help dev build format setup-env generate-secret docker-build-prod docker-build-dev docker-run-prod docker-run-dev docker-stop docker-clean compose-dev compose-prod compose-down

# Default target
help:
	@echo "Available targets:"
	@echo "  dev                  - Start development server"
	@echo "  build                - Build production frontend"
	@echo "  format               - Format code with prettier"
	@echo "  setup-env            - Setup environment files"
	@echo "  generate-secret      - Generate a secure NextAuth secret"
	@echo ""
	@echo "Docker targets:"
	@echo "  docker-build-prod    - Build production Docker image"
	@echo "  docker-build-dev     - Build development Docker image"
	@echo "  docker-run-prod      - Run production container"
	@echo "  docker-run-dev       - Run development container with hot reload"
	@echo "  docker-stop          - Stop all running containers"
	@echo "  docker-clean         - Remove all containers and images"
	@echo ""
	@echo "Docker Compose targets:"
	@echo "  compose-dev          - Start development with docker-compose"
	@echo "  compose-prod         - Start production with docker-compose"
	@echo "  compose-down         - Stop all compose services"

# Delegate most targets to frontend Makefile
dev build format setup-env generate-secret docker-build-prod docker-build-dev docker-run-prod docker-run-dev docker-stop docker-clean:
	@cd frontend && $(MAKE) $@

# Docker Compose targets (run from root)
compose-dev:
	docker-compose up --build frontend-dev

compose-prod:
	docker-compose --profile production up --build frontend-prod

compose-down:
	docker-compose down --remove-orphans

# Convenience targets
prod: docker-build-prod docker-run-prod
	@echo "Production container is running at http://localhost:3000"

dev-docker: docker-build-dev docker-run-dev
	@echo "Development container is running at http://localhost:3000" 