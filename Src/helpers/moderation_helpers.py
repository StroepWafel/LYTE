# =============================================================================
#  MODERATION MANAGEMENT FUNCTIONS
# =============================================================================

# Standard Library Imports
import json
import os

# =============================================================================

def load_banned_users(banned_users_path: str) -> list:
    """
    Load banned users list from file.
    
    Args:
        banned_users_path: Path to the banned users JSON file
        
    Returns:
        list: List of banned users
    """
    if os.path.exists(banned_users_path):
        with open(banned_users_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def load_banned_ids(banned_ids_path: str) -> list:
    """
    Load banned video IDs list from file.
    
    Args:
        banned_ids_path: Path to the banned IDs JSON file
        
    Returns:
        list: List of banned video IDs
    """
    if os.path.exists(banned_ids_path):
        with open(banned_ids_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def load_whitelisted_users(whitelisted_users_path: str) -> list:
    """
    Load whitelisted users list from file.
    
    Args:
        whitelisted_users_path: Path to the whitelisted users JSON file
        
    Returns:
        list: List of whitelisted users
    """
    if os.path.exists(whitelisted_users_path):
        with open(whitelisted_users_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def load_whitelisted_ids(whitelisted_ids_path: str) -> list:
    """
    Load whitelisted video IDs list from file.
    
    Args:
        whitelisted_ids_path: Path to the whitelisted IDs JSON file
        
    Returns:
        list: List of whitelisted video IDs
    """
    if os.path.exists(whitelisted_ids_path):
        with open(whitelisted_ids_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_banned_users(banned_users: list, banned_users_path: str) -> None:
    """Save banned users list to file."""
    with open(banned_users_path, "w", encoding="utf-8") as f:
        json.dump(banned_users, f, indent=4)

def save_banned_ids(banned_ids: list, banned_ids_path: str) -> None:
    """Save banned video IDs list to file."""
    with open(banned_ids_path, "w", encoding="utf-8") as f:
        json.dump(banned_ids, f, indent=4)

def save_whitelisted_users(whitelisted_users: list, whitelisted_users_path: str) -> None:
    """Save whitelisted users list to file."""
    with open(whitelisted_users_path, "w", encoding="utf-8") as f:
        json.dump(whitelisted_users, f, indent=4)

def save_whitelisted_ids(whitelisted_ids: list, whitelisted_ids_path: str) -> None:
    """Save whitelisted video IDs list to file."""
    with open(whitelisted_ids_path, "w", encoding="utf-8") as f:
        json.dump(whitelisted_ids, f, indent=4)