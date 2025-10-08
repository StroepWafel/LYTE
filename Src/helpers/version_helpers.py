# =============================================================================
# VERSION MANAGEMENT
# =============================================================================

# Standard Library Imports
import logging
from datetime import datetime

# Third-Party Imports
import requests  # HTTP requests

# =============================================================================

def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        version1: First version string (e.g., "1.5.0")
        version2: Second version string (e.g., "1.6.0")
        
    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    def version_tuple(v):
        # Remove any non-numeric suffixes (like "-Release", "-beta", etc.)
        # and split by dots, converting to integers
        clean_version = v.split('-')[0].split('_')[0]  # Remove suffixes after - or _
        parts = clean_version.split('.')
        
        # Convert each part to int, handling cases where parts might be empty
        result = []
        for part in parts:
            if part.isdigit():
                result.append(int(part))
            else:
                # If any part is not a digit, treat as 0
                result.append(0)
        return tuple(result)
    
    v1_tuple = version_tuple(version1)
    v2_tuple = version_tuple(version2)
    
    if v1_tuple < v2_tuple:
        return -1
    elif v1_tuple > v2_tuple:
        return 1
    else:
        return 0

def fetch_latest_version() -> str:
    """
    Fetch the latest release version from GitHub API.
    
    Returns:
        str: Latest version string, or empty string if failed
    """
    try:
        url = "https://api.github.com/repos/StroepWafel/LYTE/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        latest_version = data.get("tag_name", "")
        
        # Remove 'v' prefix if present
        if latest_version.startswith("v"):
            latest_version = latest_version[1:]
            
        logging.info(f"Latest version available: {latest_version}")
        return latest_version
        
    except Exception as e:
        logging.warning(f"Failed to fetch latest version: {e}")
        return ""
