# =============================================================================
# UPDATE MANAGEMENT UTILITIES
# =============================================================================

# Standard Library Imports
import logging
import os
from datetime import datetime

# Third-Party Imports
import requests  # HTTP requests

# Local Imports
from .version_helpers import (
    fetch_latest_version, 
    compare_versions
    )


# =============================================================================

def run_installer(app_folder: str) -> None:
    """
    Run the downloaded installer.
    
    Args:
        app_folder: Path to the application folder
    """
    try:
        installer_path = os.path.join(app_folder, "LYTE_Installer.exe")
        
        if os.path.exists(installer_path):
            logging.info("Running installer...")
            os.startfile(installer_path)  # Windows-specific
            logging.info("Installer started successfully")
        else:
            logging.error("Installer not found. Please download it first.")
            
    except Exception as e:
        logging.error(f"Error running installer: {e}")

def download_installer_worker(app_folder: str) -> None:
    """
    Worker function that downloads the installer in the background.
    
    Args:
        app_folder: Path to the application folder
    """
    try:
        installer_url = "https://github.com/StroepWafel/LYTE-NSIS-Installer/releases/download/latest/LYTE_Installer.exe"
        download_path = os.path.join(app_folder, "LYTE_Installer.exe")
        
        logging.info("Starting installer download...")
        
        response = requests.get(installer_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
        
        logging.info(f"Installer downloaded successfully to: {download_path}")
            
    except Exception as e:
        logging.error(f"Error downloading installer: {e}")

def check_for_updates(current_version: str, toast_notifications: bool) -> str:
    """
    Check for available updates and notify the user if a new version is available.
    
    Args:
        current_version: Current application version
        toast_notifications: Whether to show desktop notifications
        
    Returns:
        str: Latest version if available, empty string otherwise
    """
    try:
        latest_version = fetch_latest_version()
        if not latest_version:
            return ""
            
        if compare_versions(current_version, latest_version) < 0:
            logging.info(f"Update available! Current: {current_version}, Latest: {latest_version}")
            logging.info("To view changelog and available options, navigate to 'Help -> View update Details...'")
            
            # Show desktop notification if enabled
            if toast_notifications:
                from plyer import notification
                notification.notify(
                    title="LYTE Update Available",
                    message=f"Version {latest_version} is now available! Current version: {current_version}",
                    timeout=10
                )
            
            return latest_version
        else:
            logging.info(f"LYTE is up to date (version {current_version})")
            return ""
            
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")
        return ""
