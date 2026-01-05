"""
Polaris catalog setup module.

Provides functions to create and configure Polaris catalogs with S3/MinIO storage.
CLI is in main.py.
"""

import base64
import logging

import requests

# Initialize logger for this module
logger = logging.getLogger(__name__)

POLARIS_URL = "http://localhost:8181"
CLIENT_ID = "c208b265597a57cc"
CLIENT_SECRET = "b0d74647fdc58fa84c6ac099cd34260f"


def get_bearer_token() -> str:
    """Get OAuth2 bearer token from Polaris."""
    token_url = f"{POLARIS_URL}/api/catalog/v1/oauth/tokens"
    logger.debug(f"Requesting OAuth2 token from {token_url}")

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

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        logger.debug("Successfully obtained OAuth2 token")

        token_data = response.json()
        token = token_data["access_token"]
        logger.debug(f"Token obtained (first 20 chars): {token[:20]}...")
        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get OAuth2 token: {e}")
        raise


def delete_namespace(
    token: str, catalog_name: str = "warehouse", namespace: str = "default"
) -> bool:
    """Delete a namespace from a catalog using the Iceberg REST API."""
    url = f"{POLARIS_URL}/api/catalog/v1/{catalog_name}/namespaces/{namespace}"
    logger.debug(f"Deleting namespace '{namespace}' from catalog '{catalog_name}'")

    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            logger.info(f"Deleted namespace '{namespace}'")
            return True
        elif response.status_code == 404:
            logger.debug(f"Namespace '{namespace}' doesn't exist (404)")
            return True
        else:
            logger.warning(
                f"Delete namespace response: {response.status_code} - {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting namespace '{namespace}': {e}")
        return False


def delete_catalog_role(
    token: str, catalog_name: str = "warehouse", role_name: str = "admin_role"
) -> bool:
    """Delete a catalog role."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}/catalog-roles/{role_name}"
    logger.debug(f"Deleting catalog role '{role_name}' from catalog '{catalog_name}'")

    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            logger.info(f"Deleted catalog role '{role_name}'")
            return True
        elif response.status_code == 404:
            logger.debug(f"Catalog role '{role_name}' doesn't exist (404)")
            return True
        else:
            logger.warning(
                f"Delete catalog role response: {response.status_code} - {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting catalog role '{role_name}': {e}")
        return False


def delete_catalog(token: str, catalog_name: str = "warehouse") -> bool:
    """Delete a catalog in Polaris (must be empty first)."""
    logger.info(f"Deleting catalog '{catalog_name}'...")
    
    # First try to delete the default namespace
    delete_namespace(token, catalog_name, "default")
    # Delete the admin_role
    delete_catalog_role(token, catalog_name, "admin_role")

    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}"
    logger.debug(f"Sending DELETE request to {url}")

    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            logger.info(f"Deleted catalog '{catalog_name}'")
            return True
        elif response.status_code == 404:
            logger.debug(f"Catalog '{catalog_name}' doesn't exist (404)")
            return True
        else:
            logger.warning(
                f"Delete catalog response: {response.status_code} - {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting catalog '{catalog_name}': {e}")
        return False


def list_catalogs(token: str) -> dict:
    """List available catalogs in Polaris."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs"
    logger.debug(f"Fetching catalog list from {url}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        logger.info("Available catalogs:")
        if "catalogs" in data:
            for catalog in data["catalogs"]:
                catalog_name = catalog.get('name', 'unknown')
                logger.info(f"  - {catalog_name}")
        else:
            logger.debug(f"Unexpected response format: {data}")

        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to list catalogs: {e}")
        raise


def create_catalog(token: str, catalog_name: str = "warehouse") -> bool:
    """Create a catalog in Polaris using the management API."""
    url = f"{POLARIS_URL}/api/management/v1/catalogs"
    logger.info(f"Creating catalog '{catalog_name}'...")

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

    logger.debug(f"Catalog payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.debug(f"Create catalog response status: {response.status_code}")

        if response.status_code == 409:
            logger.info(f"Catalog '{catalog_name}' already exists")
            return True
        elif response.status_code in [200, 201]:
            logger.info(f"Created catalog: {catalog_name}")
            return True
        else:
            logger.warning(
                f"Unexpected response: {response.status_code} - {response.text}"
            )
            response.raise_for_status()

        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create catalog '{catalog_name}': {e}")
        return False


def grant_catalog_role(token: str, catalog_name: str = "warehouse") -> bool:
    """Grant catalog admin role to the root principal for full permissions."""
    logger.info(f"Granting permissions to catalog '{catalog_name}'...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # First, create a catalog role with full privileges
    catalog_role_name = "admin_role"

    # Create catalog role
    url = f"{POLARIS_URL}/api/management/v1/catalogs/{catalog_name}/catalog-roles"
    payload = {"name": catalog_role_name}

    logger.debug(f"Creating catalog role '{catalog_role_name}'...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.debug(f"Create role response: {response.status_code}")

        if response.status_code not in [200, 201, 409]:
            logger.warning("Could not create catalog role")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error creating catalog role: {e}")

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
    logger.debug(f"Granting {len(privileges)} privileges to '{catalog_role_name}'...")
    
    for privilege in privileges:
        grant_payload = {"type": "catalog", "privilege": privilege}
        try:
            response = requests.put(url, headers=headers, json=grant_payload)
            if response.status_code in [200, 201, 204]:
                logger.debug(f"Granted privilege: {privilege}")
            else:
                logger.warning(
                    f"Could not grant privilege {privilege}: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error granting privilege {privilege}: {e}")

    # Now assign the catalog role to the service_admin principal role
    url = f"{POLARIS_URL}/api/management/v1/principal-roles/service_admin/catalog-roles/{catalog_name}"
    payload = {"name": catalog_role_name}

    logger.debug(f"Assigning catalog role to service_admin...")
    try:
        response = requests.put(url, headers=headers, json=payload)
        logger.debug(f"Assign role response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error assigning catalog role: {e}")
        return False

    logger.info("Successfully granted all permissions to catalog")
    return True
