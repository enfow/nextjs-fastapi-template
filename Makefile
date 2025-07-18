# Root Makefile for Next.js FastAPI Template
.PHONY: help dev build format setup-env generate-secret docker-build-prod docker-build-dev docker-run-prod docker-run-dev docker-stop docker-clean compose-dev compose-prod compose-down
.PHONY: backend-help backend-dev backend-prod backend-install backend-setup backend-test backend-lint backend-format backend-clean
.PHONY: mongo-shell mongo-reset mongo-backup mongo-logs mongo-status
.PHONY: minio-console minio-logs minio-status minio-reset minio-backup

# Default target
help:
	@echo "Next.js FastAPI Template - Available targets:"
	@echo ""
	@echo "Frontend targets:"
	@echo "  dev                  - Start Next.js development server"
	@echo "  build                - Build production frontend"
	@echo "  format               - Format frontend code with prettier"
	@echo "  setup-env            - Setup frontend environment files"
	@echo "  generate-secret      - Generate a secure NextAuth secret"
	@echo ""
	@echo "Backend targets:"
	@echo "  backend-help         - Show all backend targets"
	@echo "  backend-dev          - Start FastAPI development server"
	@echo "  backend-prod         - Start FastAPI production server"
	@echo "  backend-install      - Install backend dependencies with uv"
	@echo "  backend-setup        - Setup backend (install + create .env)"
	@echo "  backend-test         - Run backend tests"
	@echo "  backend-lint         - Run backend linting"
	@echo "  backend-format       - Format backend code"
	@echo "  backend-clean        - Clean backend cache files"
	@echo ""
	@echo "MongoDB targets:"
	@echo "  mongo-shell          - Open MongoDB shell"
	@echo "  mongo-reset          - Reset MongoDB database"
	@echo "  mongo-backup         - Create MongoDB backup"
	@echo "  mongo-logs           - View MongoDB container logs"
	@echo "  mongo-status         - Check MongoDB connection status"
	@echo ""
	@echo "MinIO targets:"
	@echo "  minio-console        - Open MinIO web console"
	@echo "  minio-logs           - View MinIO container logs"
	@echo "  minio-status         - Check MinIO connection status"
	@echo "  minio-reset          - Reset MinIO bucket"
	@echo "  minio-backup         - Create MinIO bucket backup"
	@echo ""
	@echo "Full stack development:"
	@echo "  dev-all              - Start both frontend and backend development servers"
	@echo "  setup-all            - Setup both frontend and backend"
	@echo "  test-all             - Run all tests (frontend + backend)"
	@echo "  format-all           - Format all code (frontend + backend)"
	@echo "  clean-all            - Clean all cache files"
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
	@echo "  compose-dev          - Start full-stack development (frontend + backend)"
	@echo "  compose-backend-dev  - Start backend development only"
	@echo "  compose-frontend-dev - Start frontend development only"
	@echo "  compose-prod         - Start full-stack production (frontend + backend)"
	@echo "  compose-backend-prod - Start backend production only"
	@echo "  compose-frontend-prod- Start frontend production only"
	@echo "  compose-down         - Stop all compose services"
	@echo "  compose-logs         - View logs from all services"
	@echo "  compose-logs-backend - View backend logs only"
	@echo "  compose-logs-frontend- View frontend logs only"

# Delegate most targets to frontend Makefile
dev build format setup-env generate-secret docker-build-prod docker-build-dev docker-run-prod docker-run-dev docker-stop docker-clean:
	@cd frontend && $(MAKE) $@

# Docker Compose targets (run from root)
compose-dev:
	@echo "Starting full-stack development environment..."
	@echo "🚀 Backend API: http://localhost:8000"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "📚 API Docs: http://localhost:8000/api/docs"
	docker compose up

compose-backend-dev:
	@echo "Starting backend development only..."
	docker compose up --build backend-dev

compose-frontend-dev:
	@echo "Starting frontend development only..."
	docker compose up --build frontend-dev

compose-prod:
	@echo "Starting full-stack production environment..."
	@echo "🚀 Backend API: http://localhost:8001"
	@echo "🌐 Frontend: http://localhost:3001"
	@echo "📚 API Docs: http://localhost:8001/api/docs"
	docker compose --profile production up --build backend-prod frontend-prod

compose-backend-prod:
	@echo "Starting backend production only..."
	docker compose --profile production up --build backend-prod

compose-frontend-prod:
	@echo "Starting frontend production only..."
	docker compose --profile production up --build frontend-prod

compose-down:
	@echo "Stopping all services..."
	docker compose down --remove-orphans

compose-logs:
	docker compose logs -f

compose-logs-backend:
	docker compose logs -f backend-dev backend-prod

compose-logs-frontend:
	docker compose logs -f frontend-dev frontend-prod

compose-build-dev:
	docker compose build --no-cache frontend-dev backend-dev

compose-build-prod:
	docker compose build --no-cache frontend-prod backend-prod