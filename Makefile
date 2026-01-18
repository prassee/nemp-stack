.PHONY: help up down \
	start-minio stop-minio \
	start-polaris-db stop-polaris-db \
	start-polaris stop-polaris \
	start-polaris-console stop-polaris-console \
	start-clickhouse stop-clickhouse \
	start-mysql stop-mysql \
	status logs

# Default target
help:
	@echo "NMT Stack - Docker Compose Management"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "All Services:"
	@echo "  up                  Start all containers"
	@echo "  down                Stop all containers"
	@echo "  status              Show status of all containers"
	@echo "  logs                Show logs of all containers"
	@echo ""
	@echo "Individual Services:"
	@echo "  start-minio         Start MinIO (object storage)"
	@echo "  stop-minio          Stop MinIO"
	@echo ""
	@echo "  start-polaris-db    Start Polaris PostgreSQL database"
	@echo "  stop-polaris-db     Stop Polaris PostgreSQL database"
	@echo ""
	@echo "  start-polaris       Start Polaris (Iceberg catalog)"
	@echo "  stop-polaris        Stop Polaris"
	@echo ""
	@echo "  start-polaris-console  Start Polaris Console (web UI)"
	@echo "  stop-polaris-console   Stop Polaris Console"
	@echo ""
	@echo "  start-clickhouse    Start ClickHouse"
	@echo "  stop-clickhouse     Stop ClickHouse"
	@echo ""
	@echo "  start-mysql         Start MySQL"
	@echo "  stop-mysql          Stop MySQL"

# All services
up:
	docker compose up -d

down:
	docker compose down

status:
	docker compose ps

logs:
	docker compose logs -f

# MinIO
start-minio:
	docker compose up -d minio minio-init

stop-minio:
	docker compose stop minio minio-init
	docker compose rm -f minio-init

# Polaris DB
start-polaris-db:
	docker compose up -d polaris-db

stop-polaris-db:
	docker compose stop polaris-db

# Polaris (includes dependencies)
start-polaris:
	docker compose up -d polaris polaris-init

stop-polaris:
	docker compose stop polaris polaris-init
	docker compose rm -f polaris-init

# Polaris Console
start-polaris-console:
	docker compose up -d polaris-console

stop-polaris-console:
	docker compose stop polaris-console

# ClickHouse
start-clickhouse:
	docker compose up -d clickhouse

stop-clickhouse:
	docker compose stop clickhouse

# MySQL
start-mysql:
	docker compose up -d mysql

stop-mysql:
	docker compose stop mysql
