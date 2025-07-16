# Frontend Makefile for Docker and Development
.PHONY: help dev build format setup-env generate-secret docker-build-prod docker-build-dev docker-run-prod docker-run-dev docker-stop docker-clean

# Default target
help:
	@echo "Frontend targets:"
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

# Development
dev:
	yarn dev

build:
	yarn build

format:
	yarn prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,md}"

# Environment setup
setup-env:
	@echo "Setting up environment files..."
	@chmod +x scripts/setup-env.sh
	@bash scripts/setup-env.sh

generate-secret:
	@echo "Generated NextAuth secret:"
	@openssl rand -base64 32 || node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Docker targets
docker-build-prod:
	docker build -f Dockerfile -t nextjs-app:prod .

docker-build-dev:
	docker build -f Dockerfile.dev -t nextjs-app:dev .

docker-run-prod:
	@echo "Starting production container..."
	@if [ ! -f .env.production ]; then \
		echo "❌ Error: .env.production not found!"; \
		echo "📋 Create it from .env.production.example"; \
		exit 1; \
	fi
	docker run --rm\
		--name nextjs-prod \
		-p 3000:3000 \
		--env-file .env.production \
		nextjs-app:prod

docker-run-dev:
	@echo "Starting development container..."
	@if [ ! -f .env.local ]; then \
		echo "⚠️  No .env.local found, running setup..."; \
		make setup-env; \
	fi
	docker run --rm \
		--name nextjs-dev \
		-p 3000:3000 \
		-v "$(PWD):/app" \
		-v /app/node_modules \
		-v /app/.next \
		--env-file .env.local \
		nextjs-app:dev

docker-stop:
	@echo "Stopping all containers..."
	@docker stop nextjs-prod nextjs-dev 2>/dev/null || true
	@docker rm nextjs-prod nextjs-dev 2>/dev/null || true

docker-clean: docker-stop
	@echo "Cleaning up Docker images..."
	@docker rmi nextjs-app:prod nextjs-app:dev 2>/dev/null || true
	@docker system prune -f

# Convenience targets
prod: docker-build-prod docker-run-prod
	@echo "Production container is running at http://localhost:3000"

dev-docker: docker-build-dev docker-run-dev
	@echo "Development container is running at http://localhost:3000" 