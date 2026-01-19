.PHONY: help up down \
	start-minio stop-minio \
	start-iceberg-catalog-db stop-iceberg-catalog-db \
	start-iceberg-rest stop-iceberg-rest \
	start-clickhouse stop-clickhouse \
	start-mysql stop-mysql \
	start-spark stop-spark \
	status logs \
	podman-up podman-down \
	podman-start-minio podman-stop-minio \
	podman-start-iceberg-catalog-db podman-stop-iceberg-catalog-db \
	podman-start-iceberg-rest podman-stop-iceberg-rest \
	podman-start-clickhouse podman-stop-clickhouse \
	podman-start-mysql podman-stop-mysql \
	podman-start-spark podman-stop-spark \
	podman-status podman-logs

# Default target
help:
	@echo "NMT Stack - Docker Compose Management"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "========================"
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
	@echo ""
	@echo "Podman Compose Commands:"
	@echo "========================"
	@echo ""
	@echo "All Services:"
	@echo "  podman-up           Start all containers"
	@echo "  podman-down         Stop all containers"
	@echo "  podman-status       Show status of all containers"
	@echo "  podman-logs         Show logs of all containers"
	@echo ""
	@echo "Individual Services:"
	@echo "  podman-start-minio         Start MinIO (object storage)"
	@echo "  podman-stop-minio          Stop MinIO"
	@echo ""
	@echo "  podman-start-iceberg-catalog-db  Start Iceberg catalog PostgreSQL database"
	@echo "  podman-stop-iceberg-catalog-db   Stop Iceberg catalog PostgreSQL database"
	@echo ""
	@echo "  podman-start-iceberg-rest  Start Iceberg REST catalog"
	@echo "  podman-stop-iceberg-rest   Stop Iceberg REST catalog"
	@echo ""
	@echo "  podman-start-clickhouse    Start ClickHouse"
	@echo "  podman-stop-clickhouse     Stop ClickHouse"
	@echo ""
	@echo "  podman-start-mysql         Start MySQL"
	@echo "  podman-stop-mysql          Stop MySQL"
	@echo ""
	@echo "  podman-start-spark         Start Spark cluster (master, workers, history server)"
	@echo "  podman-stop-spark          Stop Spark cluster"

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

# ============================================================================
# Podman Compose Commands
# ============================================================================

# All services (Podman)
podman-up:
	podman-compose up -d

podman-down:
	podman-compose down

podman-status:
	podman-compose ps

podman-logs:
	podman-compose logs -f

# MinIO (Podman)
podman-start-minio:
	podman-compose up -d minio minio-init

podman-stop-minio:
	podman-compose stop minio minio-init
	podman-compose rm -f minio-init

# Iceberg Catalog DB (Podman)
podman-start-iceberg-catalog-db:
	podman-compose up -d iceberg-catalog-db

podman-stop-iceberg-catalog-db:
	podman-compose stop iceberg-catalog-db

# Iceberg REST Catalog (Podman)
podman-start-iceberg-rest:
	podman-compose up -d iceberg-rest

podman-stop-iceberg-rest:
	podman-compose stop iceberg-rest

# ClickHouse (Podman)
podman-start-clickhouse:
	podman-compose up -d clickhouse

podman-stop-clickhouse:
	podman-compose stop clickhouse

# MySQL (Podman)
podman-start-mysql:
	podman-compose up -d mysql

podman-stop-mysql:
	podman-compose stop mysql

# Spark (Podman)
podman-start-spark:
	podman-compose up -d spark-master spark-worker-1 spark-worker-2 spark-history-server

podman-stop-spark:
	podman-compose stop spark-master spark-worker-1 spark-worker-2 spark-history-server
