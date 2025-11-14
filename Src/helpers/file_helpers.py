# =============================================================================
# FILE AND CONFIGURATION FUNCTIONS
# =============================================================================

# Standard Library Imports
import json
import logging
import os
import sys
from datetime import datetime

# =============================================================================

def get_app_folder() -> str:
    """
    Determine the application folder path.
    
    Returns:
        str: Path to the application directory (user data dir if frozen, script dir otherwise)
    """
    if getattr(sys, 'frozen', False):
        # When compiled with PyInstaller, use a user-writable directory
        # This avoids permission issues when installed in Program Files
        if sys.platform == 'win32':
            # Use LOCALAPPDATA on Windows (AppData\Local\LYTE\)
            appdata_dir = os.getenv('LOCALAPPDATA')
            if appdata_dir:
                app_folder = os.path.join(appdata_dir, 'LYTE')
                os.makedirs(app_folder, exist_ok=True)
                return app_folder
        # Fallback for other platforms or if LOCALAPPDATA is not set
        # Try to use a user-writable location relative to the executable
        executable_dir = os.path.dirname(sys.executable)
        # Check if we can write to the executable directory
        try:
            test_file = os.path.join(executable_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return executable_dir
        except (OSError, PermissionError):
            # Can't write to executable dir, use user home directory
            home_dir = os.path.expanduser('~')
            app_folder = os.path.join(home_dir, '.lyte')
            os.makedirs(app_folder, exist_ok=True)
            return app_folder
    
    # For development/script mode, find the directory containing main.py
    # Start by checking if we can find main.py relative to this file's location
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if main.py is in the parent directory of this file (Src directory)
    parent_dir = os.path.dirname(current_file_dir)
    main_py_path = os.path.join(parent_dir, 'main.py')
    if os.path.exists(main_py_path):
        return parent_dir
    
    # If not found, search from current working directory up the tree
    current_dir = os.path.abspath(os.getcwd())
    search_dir = current_dir
    
    while True:
        main_py_path = os.path.join(search_dir, 'main.py')
        if os.path.exists(main_py_path):
            return search_dir
        
        # Move up one directory
        parent_dir = os.path.dirname(search_dir)
        if parent_dir == search_dir:  # Reached root directory
            break
        search_dir = parent_dir
    
    # Final fallback: return the directory containing this file (helpers directory)
    # and go up one level to get the Src directory
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_file_exists(filepath: str, default_content) -> None:
    """
    Create a file with default content if it doesn't exist.
    
    Args:
        filepath: Path to the file to create
        default_content: Default content to write to the file
    """
    if not os.path.isfile(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)
        logging.info(f"Created missing file: {filepath}")

def ensure_json_valid(filepath: str, default_content: dict) -> None:
    """
    Validate and clean a JSON configuration file.
    
    This function ensures the JSON file is valid and contains only expected keys.
    If the file is corrupted or contains extra keys, it will be cleaned up.
    
    Args:
        filepath: Path to the JSON file to validate
        default_content: Default configuration structure to validate against
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # Reset to defaults if file is corrupted
                with open(filepath, 'w', encoding='utf-8') as fw:
                    json.dump(default_content, fw, indent=4)
                logging.warning(f"Invalid JSON in {filepath}. Resetting to default.")
                return

        modified = False
        cleaned_data = {}

        # Copy over valid keys from default_config
        for key, default_value in default_content.items():
            if key in data:
                cleaned_data[key] = data[key]
            else:
                cleaned_data[key] = default_value
                modified = True
                logging.info(f"Added missing key '{key}' to {filepath}")

        # Check for and remove extra keys
        extra_keys = set(data.keys()) - set(default_content.keys())
        if extra_keys:
            modified = True
            logging.info(f"Removing extra keys from {filepath}: {extra_keys}")

        if modified:
            # Create a backup before making changes
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{filepath}.backup_{timestamp}.json"
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                json.dump(data, backup_file, indent=4)
            logging.info(f"Backed up original config file to {backup_path}")

            # Write cleaned data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=4)
            logging.info(f"Successfully cleaned and updated {filepath}")

    except Exception as e:
        logging.error(f"Error validating JSON file {filepath}: {e}")