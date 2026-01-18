"""
Polaris catalog setup module.

Provides functions to create and configure Polaris catalogs with S3/MinIO storage.
CLI is in main.py.
"""

import base64

import requests

POLARIS_URL = "http://localhost:8181"
CLIENT_ID = "75e97f33fddb4e7f"
CLIENT_SECRET = "4c4fdd288ab66024d90455554954b037"


def get_bearer_token() -> str:
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


def delete_namespace(
    token: str, catalog_name: str = "warehouse", namespace: str = "default"
) -> bool:
    """Delete a namespace from a catalog using the Iceberg REST API."""
    url = f"{POLARIS_URL}/api/catalog/v1/{catalog_name}/namespaces/{namespace}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"  Deleted namespace '{namespace}'")
        return True
    elif response.status_code == 404:
        print(f"  Namespace '{namespace}' doesn't exist")
        return True
    else:
        print(f"  Delete namespace response: {response.status_code} - {response.text}")
        return False


def delete_catalog_role(
    token: str, catalog_name: str = "warehouse", role_name: str = "admin_role"
) -> bool:
    """Delete a catalog role."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}/catalog-roles/{role_name}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"  Deleted catalog role '{role_name}'")
        return True
    elif response.status_code == 404:
        print(f"  Catalog role '{role_name}' doesn't exist")
        return True
    else:
        print(
            f"  Delete catalog role response: {response.status_code} - {response.text}"
        )
        return False


def delete_catalog(token: str, catalog_name: str = "warehouse") -> bool:
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
        print(f"  Deleted catalog '{catalog_name}'")
        return True
    elif response.status_code == 404:
        print(f"  Catalog '{catalog_name}' doesn't exist")
        return True
    else:
        print(f"  Delete response: {response.status_code} - {response.text}")
        return False


def list_catalogs(token: str) -> dict:
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


def create_catalog(token: str, catalog_name: str = "warehouse") -> bool:
    """Create a catalog in Polaris using the management API."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Polaris catalog creation payload format
    # Use S3 storage type with stsUnavailable=true for MinIO (no STS credential vending)
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
        print(f"  Catalog '{catalog_name}' already exists")
        return True
    elif response.status_code in [200, 201]:
        print(f"  Created catalog: {catalog_name}")
        return True
    else:
        response.raise_for_status()

    return True


def grant_catalog_role(token: str, catalog_name: str = "warehouse") -> bool:
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
        print("    Warning: Could not create catalog role")

    # Grant privileges to the catalog role
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
            print(f"    Granted {privilege}")
        else:
            print(f"    Warning: Could not grant {privilege}: {response.status_code}")

    # Now assign the catalog role to the service_admin principal role
    url = f"{POLARIS_URL}/api/management/v1/principal-roles/service_admin/catalog-roles/{catalog_name}"
    payload = {"name": catalog_role_name}

    print(f"  Assigning catalog role to service_admin...")
    response = requests.put(url, headers=headers, json=payload)
    print(f"    Response: {response.status_code} - {response.text}")

    return True


if __name__ == "__main__":
    token = get_bearer_token()
    grant_catalog_role(token, "warehouse")
    print(f"Obtained bearer token: {token}...")
    print(list_catalogs(token))
