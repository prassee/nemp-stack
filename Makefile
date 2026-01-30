.PHONY: help up down \
	start-minio stop-minio \
	start-lakekeeper-db stop-lakekeeper-db \
	start-lakekeeper stop-lakekeeper \
	start-clickhouse stop-clickhouse \
	start-mysql stop-mysql \
		status logs \
	podman-up podman-down \
	podman-start-minio podman-stop-minio \
	podman-start-lakekeeper-db podman-stop-lakekeeper-db \
	podman-start-lakekeeper podman-stop-lakekeeper \
	podman-start-clickhouse podman-stop-clickhouse \
	podman-start-mysql podman-stop-mysql \
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
	@echo "  start-lakekeeper-db       Start LakeKeeper PostgreSQL database"
	@echo "  stop-lakekeeper-db        Stop LakeKeeper PostgreSQL database"
	@echo ""
	@echo "  start-lakekeeper          Start LakeKeeper Iceberg catalog (with bootstrap and warehouse init)"
	@echo "  stop-lakekeeper           Stop LakeKeeper Iceberg catalog"
	@echo ""
	@echo "  start-clickhouse    Start ClickHouse"
	@echo "  stop-clickhouse     Stop ClickHouse"
	@echo ""
	@echo "  start-mysql         Start MySQL"
	@echo "  stop-mysql          Stop MySQL"
	@echo ""
	@echo ""
	@echo ""
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
	@echo "  podman-start-lakekeeper-db       Start LakeKeeper PostgreSQL database"
	@echo "  podman-stop-lakekeeper-db        Stop LakeKeeper PostgreSQL database"
	@echo ""
	@echo "  podman-start-lakekeeper          Start LakeKeeper Iceberg catalog (with bootstrap and warehouse init)"
	@echo "  podman-stop-lakekeeper           Stop LakeKeeper Iceberg catalog"
	@echo ""
	@echo "  podman-start-clickhouse    Start ClickHouse"
	@echo "  podman-stop-clickhouse     Stop ClickHouse"
	@echo ""
	@echo "  podman-start-mysql         Start MySQL"
	@echo "  podman-stop-mysql          Stop MySQL"
	@echo ""
	@echo ""
	@echo ""
	@echo ""
	@echo ""

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

# LakeKeeper DB
start-lakekeeper-db:
	docker compose up -d lakekeeper-db

stop-lakekeeper-db:
	docker compose stop lakekeeper-db

# LakeKeeper Iceberg Catalog
start-lakekeeper:
	docker compose up -d lakekeeper-db lakekeeper-migrate lakekeeper lakekeeper-bootstrap lakekeeper-warehouse

stop-lakekeeper:
	docker compose stop lakekeeper lakekeeper-migrate lakekeeper-bootstrap lakekeeper-warehouse
	docker compose rm -f lakekeeper-migrate lakekeeper-bootstrap lakekeeper-warehouse

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

# LakeKeeper DB (Podman)
podman-start-lakekeeper-db:
	podman-compose up -d lakekeeper-db

podman-stop-lakekeeper-db:
	podman-compose stop lakekeeper-db

# LakeKeeper Iceberg Catalog (Podman)
podman-start-lakekeeper:
	podman-compose up -d lakekeeper-db lakekeeper

podman-stop-lakekeeper:
	podman-compose stop lakekeeper lakekeeper-db
	podman-compose rm -f lakekeeper lakekeeper-db

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


podman-olake-discover-mysql:
	podman run --rm \
	--network nmt-stack_default \
	--name source-mysql \
	-v $(CURDIR)/olake-config/config:/mnt/config \
	olakego/source-mysql:latest discover --config /mnt/config/source.json >> $(CURDIR)/olake-config/config/streams.json

podman-olake-sync-mysql:
	podman run --rm \
	--network nmt-stack_default \
	--name source-mysql \
	-v $(CURDIR)/olake-config/config:/mnt/config \
	olakego/source-mysql:latest sync --config /mnt/config/source.json --streams /mnt/config/streams.json --destination /mnt/config/destination.json 

podman-olake-sync-state-mysql:
	podman run --rm \
	--network nmt-stack_default \
	--name source-mysql \
	-v $(CURDIR)/olake-config/config:/mnt/config \
	olakego/source-mysql:latest sync --config /mnt/config/source.json --streams /mnt/config/streams.json --destination /mnt/config/destination.json --state /mnt/config/state.json 
