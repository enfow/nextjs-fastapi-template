# Backend Makefile for FastAPI application with UV
.PHONY: help install dev prod test lint format clean build docker-build docker-run docker-stop setup
.PHONY: mongo-shell mongo-reset mongo-backup mongo-restore mongo-restore-specific mongo-logs mongo-status
.PHONY: minio-console minio-logs minio-status minio-reset minio-backup

# Default target
help:
	@echo "Backend FastAPI Application - Available targets:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install              - Install all dependencies with uv"
	@echo "  install-dev          - Install with dev dependencies"
	@echo "  setup                - Setup project (install + create .env)"
	@echo ""
	@echo "Development:"
	@echo "  dev                  - Start development server with auto-reload"
	@echo "  prod                 - Start production server"
	@echo "  shell                - Open Python shell in virtual environment"
	@echo ""
	@echo "Code Quality:"
	@echo "  test                 - Run tests with pytest"
	@echo "  test-cov             - Run tests with coverage report"
	@echo "  lint                 - Run all linting (flake8, mypy)"
	@echo "  format               - Format code (black, isort)"
	@echo "  format-check         - Check code formatting without making changes"
	@echo ""
	@echo "Database:"
	@echo "  db-upgrade           - Run database migrations"
	@echo "  db-reset             - Reset database (delete and recreate)"
	@echo ""
	@echo "MongoDB:"
	@echo "  mongo-shell          - Open MongoDB shell (mongosh)"
	@echo "  mongo-reset          - Reset MongoDB database (drop all collections)"
	@echo "  mongo-backup         - Create MongoDB backup"
	@echo "  mongo-restore        - Restore MongoDB from backup"
	@echo "  mongo-logs           - View MongoDB container logs"
	@echo "  mongo-status         - Check MongoDB connection status"
	@echo ""
	@echo "MinIO:"
	@echo "  minio-console        - Open MinIO web console"
	@echo "  minio-logs           - View MinIO container logs"
	@echo "  minio-status         - Check MinIO connection status"
	@echo "  minio-reset          - Reset MinIO bucket (delete all objects)"
	@echo "  minio-backup         - Create MinIO bucket backup"
	@echo ""
	@echo "Utilities:"
	@echo "  clean                - Clean cache and temporary files"
	@echo "  build                - Build application (if needed)"
	@echo "  deps                 - Show dependency tree"
	@echo "  outdated             - Show outdated packages"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build         - Build Docker image"
	@echo "  docker-run           - Run Docker container"
	@echo "  docker-stop          - Stop Docker container"

# Setup & Installation
install:
	@echo "Installing dependencies with uv..."
	uv sync

install-dev:
	@echo "Installing with dev dependencies..."
	uv sync --all-extras

setup: install
	@echo "Setting up project..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from example..."; \
		echo "DATABASE_URL=sqlite:///./app.db" > .env; \
		echo "API_HOST=0.0.0.0" >> .env; \
		echo "API_PORT=8000" >> .env; \
		echo "API_RELOAD=true" >> .env; \
		echo "LOG_LEVEL=info" >> .env; \
		echo "✅ .env file created"; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi

# Development
dev:
	@echo "Starting development server..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

prod:
	@echo "Starting production server..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

shell:
	@echo "Opening Python shell..."
	uv run python

# Code Quality
test:
	@echo "Running tests..."
	uv run pytest

test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html

lint:
	@echo "Running linting..."
	uv run ruff check src/

format:
	uv run ruff format src/

format-check:
	@echo "Checking code formatting..."
	uv run ruff check src/

# Database
db-upgrade:
	@echo "Running database migrations..."
	uv run alembic upgrade head

db-reset:
	@echo "Resetting database..."
	@if [ -f app.db ]; then rm app.db; echo "Deleted app.db"; fi
	@if [ -f test.db ]; then rm test.db; echo "Deleted test.db"; fi
	uv run python -c "from src.database import create_tables; create_tables(); print('✅ Database tables created')"

# MongoDB
mongo-shell:
	@echo "Opening MongoDB shell..."
	docker exec -it mongodb-compose mongosh -u admin -p password123 --authenticationDatabase admin

mongo-reset:
	@echo "Resetting MongoDB database..."
	docker exec -it mongodb-compose mongosh -u admin -p password123 --authenticationDatabase admin --eval "use fastapi_db; db.dropDatabase()"

mongo-backup:
	@echo "Creating MongoDB backup..."
	mkdir -p ./backups
	docker exec mongodb-compose mongodump --authenticationDatabase admin -u admin -p password123 --db fastapi_db --out /backup/$(shell date +%Y%m%d_%H%M%S)
	docker cp mongodb-compose:/backup/$(shell date +%Y%m%d_%H%M%S) ./backups/

mongo-restore:
	@echo "Please specify backup date (format: YYYYMMDD_HHMMSS):"
	@echo "Available backups:"
	@ls -la ./backups/ 2>/dev/null || echo "No backups found"
	@echo "Use: make mongo-restore-specific BACKUP=YYYYMMDD_HHMMSS"

mongo-restore-specific:
	@echo "Restoring MongoDB from backup $(BACKUP)..."
	docker cp ./backups/$(BACKUP) mongodb-compose:/backup/
	docker exec mongodb-compose mongorestore --authenticationDatabase admin -u admin -p password123 --db fastapi_db /backup/$(BACKUP)/fastapi_db/

mongo-logs:
	@echo "Viewing MongoDB container logs..."
	docker logs mongodb-compose -f

mongo-status:
	@echo "Checking MongoDB connection status..."
	docker exec mongodb-compose mongosh -u admin -p password123 --authenticationDatabase admin --eval "db.adminCommand('ping')"

# MinIO
minio-console:
	@echo "MinIO web console is available at: http://localhost:9001"
	@echo "Username: minioadmin"
	@echo "Password: minioadmin123"
	@echo "Opening browser..."
	@which xdg-open > /dev/null && xdg-open http://localhost:9001 || echo "Please open http://localhost:9001 in your browser"

minio-logs:
	@echo "Viewing MinIO container logs..."
	docker logs minio-compose -f

minio-status:
	@echo "Checking MinIO connection status..."
	@docker exec minio-compose sh -c "curl -f http://localhost:9000/minio/health/live" && echo "✅ MinIO is healthy" || echo "❌ MinIO is not responding"

minio-reset:
	@echo "Resetting MinIO bucket (fastapi-images)..."
	@echo "⚠️  This will delete ALL images! Press Ctrl+C to cancel."
	@sleep 5
	docker exec minio-compose mc rm --recursive --force minio/fastapi-images/ || echo "Bucket already empty"

minio-backup:
	@echo "Creating MinIO bucket backup..."
	mkdir -p ./backups/minio
	docker exec minio-compose mc mirror /data/fastapi-images /backup/$(shell date +%Y%m%d_%H%M%S) || echo "Backup failed"

# Utilities
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleaned cache and temporary files"

build:
	@echo "Building application..."
	@echo "ℹ️  No build step required for FastAPI application"

deps:
	@echo "Showing dependency tree..."
	uv tree

outdated:
	@echo "Checking for outdated packages..."
	uv tree --outdated

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t fastapi-backend .

docker-run:
	@echo "Running Docker container..."
	docker run --rm --name fastapi-backend -p 8000:8000 fastapi-backend

docker-stop:
	@echo "Stopping Docker container..."
	docker stop fastapi-backend 2>/dev/null || true

# Quality assurance target that runs multiple checks
qa: format-check lint test
	@echo "✅ Quality assurance checks passed"

# Development workflow - setup and start
start: setup dev

# Production workflow - install and run
deploy: install prod 