#!/bin/bash

# DataLakeCatalog Integration Test Script
# This script verifies the ClickHouse + Lakekeeper + MinIO integration

set -e

echo "=============================================="
echo "DataLakeCatalog Integration Test"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if all services are running
echo -e "${YELLOW}[1/5] Checking service health...${NC}"
echo ""

services=("minio" "lakekeeper-db" "lakekeeper" "clickhouse")

for service in "${services[@]}"; do
    if podman ps | grep -q "$service"; then
        echo -e "${GREEN}✓${NC} $service is running"
    else
        echo -e "${RED}✗${NC} $service is NOT running"
        exit 1
    fi
done

echo ""

# Test 2: Check Lakekeeper connectivity
echo -e "${YELLOW}[2/5] Testing Lakekeeper REST API...${NC}"
echo ""

if curl -s http://localhost:8181/catalog/v1/config?warehouse=default | grep -q "overrides"; then
    echo -e "${GREEN}✓${NC} Lakekeeper REST API is responding"
else
    echo -e "${RED}✗${NC} Lakekeeper REST API is not responding"
    exit 1
fi

echo ""

# Test 3: Check ClickHouse connectivity
echo -e "${YELLOW}[3/5] Testing ClickHouse connectivity...${NC}"
echo ""

if podman exec clickhouse clickhouse-client --query "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} ClickHouse is responding"
else
    echo -e "${RED}✗${NC} ClickHouse is not responding"
    exit 1
fi

echo ""

# Test 4: Check if iceberg_catalog database exists
echo -e "${YELLOW}[4/5] Checking DataLakeCatalog database...${NC}"
echo ""

databases=$(podman exec clickhouse clickhouse-client --query "SHOW DATABASES;" 2>&1)

if echo "$databases" | grep -q "iceberg_catalog"; then
    echo -e "${GREEN}✓${NC} DataLakeCatalog database exists"
    echo ""
    echo "Available databases:"
    echo "$databases" | grep -E "^(default|iceberg_catalog|system)"
else
    echo -e "${RED}✗${NC} DataLakeCatalog database NOT found"
    echo "Available databases:"
    echo "$databases"
    exit 1
fi

echo ""

# Test 5: Check if we can query the iceberg_catalog
echo -e "${YELLOW}[5/5] Querying iceberg_catalog...${NC}"
echo ""

query_result=$(podman exec clickhouse clickhouse-client --query "USE iceberg_catalog; SHOW TABLES;" 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Successfully queried iceberg_catalog"
    echo ""
    if [ -z "$query_result" ]; then
        echo -e "${YELLOW}ℹ${NC} No tables found (empty warehouse - this is normal if no data created yet)"
    else
        echo "Tables found:"
        echo "$query_result"
    fi
else
    echo -e "${RED}✗${NC} Failed to query iceberg_catalog"
    echo "Error: $query_result"
    exit 1
fi

echo ""
echo "=============================================="
echo -e "${GREEN}All tests passed! ✓${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Create Iceberg tables in Lakekeeper"
echo "2. Query them using ClickHouse:"
echo ""
echo "   podman exec clickhouse clickhouse-client"
echo "   > USE iceberg_catalog;"
echo "   > SHOW TABLES;"
echo "   > SELECT * FROM \`namespace.table\` LIMIT 10;"
echo ""
echo "For more information, see DATALAKECATALOG_SETUP.md"
echo ""
