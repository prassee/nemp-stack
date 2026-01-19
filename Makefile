.PHONY: help up down \
	start-minio stop-minio \
	start-iceberg-catalog-db stop-iceberg-catalog-db \
	start-iceberg-rest stop-iceberg-rest \
	start-clickhouse stop-clickhouse \
	start-mysql stop-mysql \
	start-spark stop-spark \
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
	@echo "  start-iceberg-catalog-db  Start Iceberg catalog PostgreSQL database"
	@echo "  stop-iceberg-catalog-db   Stop Iceberg catalog PostgreSQL database"
	@echo ""
	@echo "  start-iceberg-rest  Start Iceberg REST catalog"
	@echo "  stop-iceberg-rest   Stop Iceberg REST catalog"
	@echo ""
	@echo "  start-clickhouse    Start ClickHouse"
	@echo "  stop-clickhouse     Stop ClickHouse"
	@echo ""
	@echo "  start-mysql         Start MySQL"
	@echo "  stop-mysql          Stop MySQL"
	@echo ""
	@echo "  start-spark         Start Spark cluster (master, workers, history server)"
	@echo "  stop-spark          Stop Spark cluster"

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

# Iceberg Catalog DB
start-iceberg-catalog-db:
	docker compose up -d iceberg-catalog-db

stop-iceberg-catalog-db:
	docker compose stop iceberg-catalog-db

# Iceberg REST Catalog
start-iceberg-rest:
	docker compose up -d iceberg-rest

stop-iceberg-rest:
	docker compose stop iceberg-rest

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

# Spark
start-spark:
	docker compose up -d spark-master spark-worker-1 spark-worker-2 spark-history-server

stop-spark:
	docker compose stop spark-master spark-worker-1 spark-worker-2 spark-history-server
