#!/usr/bin/env python3
"""
Setup script to create Polaris catalog and warehouse.
"""
import requests
import base64

POLARIS_URL = "http://localhost:8181"
# a3cad0a2fd1a31ddv:91d04e5ec30dc740aa3410e322ce7503
CLIENT_ID = "a3cad0a2fd1a31dd"
CLIENT_SECRET = "91d04e5ec30dc740aa3410e322ce7503"


def get_bearer_token():
    """Get OAuth2 bearer token from Polaris."""
    token_url = f"{POLARIS_URL}/api/catalog/v1/oauth/tokens"

    # Use client credentials flow
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "PRINCIPAL_ROLE:ALL",
    }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()

    token_data = response.json()
    return token_data["access_token"]


def delete_namespace(token, catalog_name="warehouse", namespace="default"):
    """Delete a namespace from a catalog using the Iceberg REST API."""
    url = f"{POLARIS_URL}/api/catalog/v1/{catalog_name}/namespaces/{namespace}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"  ✓ Deleted namespace '{namespace}'")
        return True
    elif response.status_code == 404:
        print(f"  Namespace '{namespace}' doesn't exist")
        return True
    else:
        print(f"  Delete namespace response: {response.status_code} - {response.text}")
        return False


def delete_catalog_role(token, catalog_name="warehouse", role_name="admin_role"):
    """Delete a catalog role."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}/catalog-roles/{role_name}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"  ✓ Deleted catalog role '{role_name}'")
        return True
    elif response.status_code == 404:
        print(f"  Catalog role '{role_name}' doesn't exist")
        return True
    else:
        print(
            f"  Delete catalog role response: {response.status_code} - {response.text}"
        )
        return False


def delete_catalog(token, catalog_name="warehouse"):
    """Delete a catalog in Polaris (must be empty first)."""
    # First try to delete the default namespace
    delete_namespace(token, catalog_name, "default")
    # Delete the admin_role
    delete_catalog_role(token, catalog_name, "admin_role")

    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"  ✓ Deleted catalog '{catalog_name}'")
        return True
    elif response.status_code == 404:
        print(f"  Catalog '{catalog_name}' doesn't exist")
        return True
    else:
        print(f"  Delete response: {response.status_code} - {response.text}")
        return False


def list_catalogs(token):
    """List available catalogs in Polaris."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    print("Available catalogs:")
    if "catalogs" in data:
        for catalog in data["catalogs"]:
            print(f"  - {catalog.get('name', 'unknown')}")
    else:
        print(f"  Response: {data}")

    return data


def create_catalog(token, catalog_name="warehouse"):
    """Create a catalog in Polaris using the management API."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Polaris catalog creation payload format
    # Use S3 storage type with stsUnavailable=true for MinIO (no STS credential vending)
    # See: https://github.com/apache/polaris/blob/main/spec/polaris-management-service.yml
    payload = {
        "name": catalog_name,
        "type": "INTERNAL",
        "storageConfigInfo": {
            "storageType": "S3",
            "allowedLocations": ["s3://warehouse/"],
            # MinIO endpoint (from Polaris container perspective)
            "endpoint": "http://minio:9000",
            # Disable STS credential vending - MinIO doesn't support STS
            "stsUnavailable": True,
            # Use path-style access for MinIO
            "pathStyleAccess": True,
            # AWS region
            "region": "us-east-1",
        },
        "properties": {"default-base-location": "s3://warehouse/"},
    }

    print(f"  Creating catalog '{catalog_name}'...")
    print(f"  Payload: {payload}")

    response = requests.post(url, headers=headers, json=payload)

    print(f"  Response status: {response.status_code}")
    print(f"  Response body: {response.text}")

    if response.status_code == 409:
        print(f"  ✓ Catalog '{catalog_name}' already exists")
        return True
    elif response.status_code in [200, 201]:
        print(f"  ✓ Created catalog: {catalog_name}")
        return True
    else:
        response.raise_for_status()

    return True


def grant_catalog_role(token, catalog_name="warehouse"):
    """Grant catalog admin role to the root principal for full permissions."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # First, create a catalog role with full privileges
    catalog_role_name = "admin_role"

    # Create catalog role
    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}/catalog-roles"
    payload = {"name": catalog_role_name}

    print(f"  Creating catalog role '{catalog_role_name}'...")
    response = requests.post(url, headers=headers, json=payload)
    print(f"    Response: {response.status_code} - {response.text}")

    if response.status_code not in [200, 201, 409]:
        print(f"    Warning: Could not create catalog role")

    # Grant privileges to the catalog role
    # Grant TABLE_WRITE_DATA, TABLE_CREATE, NAMESPACE_CREATE etc
    privileges = [
        "TABLE_CREATE",
        "TABLE_DROP",
        "TABLE_READ_DATA",
        "TABLE_WRITE_DATA",
        "TABLE_READ_PROPERTIES",
        "TABLE_WRITE_PROPERTIES",
        "TABLE_LIST",
        "NAMESPACE_CREATE",
        "NAMESPACE_DROP",
        "NAMESPACE_READ_PROPERTIES",
        "NAMESPACE_WRITE_PROPERTIES",
        "NAMESPACE_LIST",
        "VIEW_CREATE",
        "VIEW_DROP",
        "VIEW_LIST",
        "CATALOG_MANAGE_ACCESS",
        "CATALOG_MANAGE_CONTENT",
        "CATALOG_MANAGE_METADATA",
        "TABLE_FULL_METADATA",
    ]

    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}/catalog-roles/{catalog_role_name}/grants"
    for privilege in privileges:
        grant_payload = {"type": "catalog", "privilege": privilege}
        response = requests.put(url, headers=headers, json=grant_payload)
        if response.status_code in [200, 201, 204]:
            print(f"    ✓ Granted {privilege}")
        else:
            print(f"    Warning: Could not grant {privilege}: {response.status_code}")

    # Now assign the catalog role to the service_admin principal role
    url = f"{POLARIS_URL}/api/management/v1/principal-roles/service_admin/catalog-roles/{catalog_name}"
    payload = {"name": catalog_role_name}

    print(f"  Assigning catalog role to service_admin...")
    response = requests.put(url, headers=headers, json=payload)
    print(f"    Response: {response.status_code} - {response.text}")

    return True


def main():
    """Main setup function."""
    print("Setting up Polaris...")

    try:
        print("1. Getting OAuth2 token...")
        token = get_bearer_token()
        print(f"   ✓ Got token: {token[:20]}...")

        print("2. Listing existing catalogs...")
        list_catalogs(token)

        print("3. Deleting existing 'warehouse' catalog (if exists)...")
        delete_catalog(token, "warehouse")

        print("4. Creating 'warehouse' catalog with FILE storage...")
        create_catalog(token, "warehouse")

        print("5. Granting permissions to catalog...")
        grant_catalog_role(token, "warehouse")

        print("6. Verifying catalog was created...")
        list_catalogs(token)

        print("\n✓ Setup complete! You can now run main.py")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
