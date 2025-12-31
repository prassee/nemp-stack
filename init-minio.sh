#!/bin/bash
# Initialize MinIO bucket for Nessie

# Wait for MinIO to be ready
sleep 10

# Create the warehouse bucket if it doesn't exist
mc alias set minio http://localhost:9000 minioadmin minioadmin

# Create warehouse bucket
mc mb minio/warehouse --ignore-existing

echo "MinIO warehouse bucket created successfully"
