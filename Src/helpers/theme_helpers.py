# =============================================================================
# THEME MANAGEMENT FUNCTIONS (Framework-agnostic)
# =============================================================================

# Standard Library Imports
import json
import logging
import os
import sys

# =============================================================================

# Global theme state (will be initialized by init_theme_system)
AVAILABLE_THEMES: dict = {}
CURRENT_THEME: str = "dark_theme"
THEMES_FOLDER: str = ""

# Callback for applying theme to GUI (registered by GUI module)
_theme_applier = None


def register_theme_applier(applier) -> None:
    """Register a callback to apply themes. Called by the GUI module."""
    global _theme_applier
    _theme_applier = applier


def init_theme_system(themes_folder: str) -> None:
    """
    Initialize the theme system with the themes folder path.

    Args:
        themes_folder: Path to the themes directory
    """
    global THEMES_FOLDER
    THEMES_FOLDER = themes_folder
    os.makedirs(THEMES_FOLDER, exist_ok=True)


def _register_theme(themes: dict, theme_name: str, display_name: str, filename: str,
                    theme_type: str, path_key: str, path_value: str) -> None:
    """Helper to register a theme in the themes dict."""
    themes[theme_name] = {
        "file": filename,
        "display_name": display_name,
        "theme_type": theme_type,
        path_key: path_value
    }


def discover_themes() -> dict:
    """
    Scan the themes folder and discover all available theme files.
    Supports both JSON themes (converted to QSS) and raw .qss stylesheets.
    Checks both PyInstaller bundle location and user app folder.

    Returns:
        dict: Dictionary mapping theme names to theme info
    """
    themes = {}

    def scan_folder(folder: str, path_key: str) -> None:
        if not os.path.exists(folder):
            return
        try:
            for filename in os.listdir(folder):
                if filename.endswith('.json') and not filename.endswith('.json.demo'):
                    theme_name = filename[:-5]
                    theme_path = os.path.join(folder, filename)
                    try:
                        with open(theme_path, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                        display_name = theme_data.get('name', theme_name.replace('_', ' ').title())
                        _register_theme(themes, theme_name, display_name, filename, "json", path_key, theme_path)
                    except (json.JSONDecodeError, IOError) as e:
                        logging.warning(f"Failed to load theme {filename}: {e}")

                elif filename.endswith('.qss'):
                    theme_name = filename[:-4]
                    theme_path = os.path.join(folder, filename)
                    display_name = theme_name.replace('_', ' ').title()
                    _register_theme(themes, theme_name, display_name, filename, "qss", path_key, theme_path)
        except Exception as e:
            logging.warning(f"Error scanning themes folder {folder}: {e}")

    # Check PyInstaller bundle location first (for bundled themes)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_themes_folder = os.path.join(sys._MEIPASS, 'themes')
        scan_folder(bundle_themes_folder, "bundle_path")

    # Check user app folder (for custom themes - these override bundled themes)
    if THEMES_FOLDER:
        scan_folder(THEMES_FOLDER, "user_path")

    return themes


def load_theme_from_file(theme_name: str) -> dict | None:
    """
    Load theme configuration from a JSON file.
    Checks user folder first, then PyInstaller bundle location.

    Args:
        theme_name: Name of the theme file (without .json extension)

    Returns:
        dict: Theme configuration with 'colors' and 'styles' keys, or None
    """
    if THEMES_FOLDER:
        user_theme_path = os.path.join(THEMES_FOLDER, f"{theme_name}.json")
        if os.path.exists(user_theme_path):
            try:
                with open(user_theme_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Error loading theme from {user_theme_path}: {e}")
                return None

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_theme_path = os.path.join(sys._MEIPASS, 'themes', f"{theme_name}.json")
        if os.path.exists(bundle_theme_path):
            try:
                with open(bundle_theme_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Error loading bundled theme: {e}")
                return None

    logging.warning(f"Theme file not found: {theme_name}.json")
    return None


def load_qss_from_file(theme_name: str) -> str | None:
    """
    Load a raw QSS (Qt stylesheet) theme from file.
    Used when theme_type is "qss".

    Args:
        theme_name: Name of the theme file (without .qss extension)

    Returns:
        str: Raw QSS content, or None if not found
    """
    # User folder first
    if THEMES_FOLDER:
        user_path = os.path.join(THEMES_FOLDER, f"{theme_name}.qss")
        if os.path.exists(user_path):
            try:
                with open(user_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError as e:
                logging.error(f"Error loading QSS theme from {user_path}: {e}")
                return None

    # Bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_path = os.path.join(sys._MEIPASS, 'themes', f"{theme_name}.qss")
        if os.path.exists(bundle_path):
            try:
                with open(bundle_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError as e:
                logging.error(f"Error loading bundled QSS theme: {e}")
                return None

    logging.warning(f"QSS theme file not found: {theme_name}.qss")
    return None


def get_theme_type(theme_name: str) -> str:
    """Return 'json' or 'qss' for the given theme. Defaults to 'json' if unknown."""
    info = AVAILABLE_THEMES.get(theme_name, {})
    return info.get("theme_type", "json")


def create_default_theme_files() -> None:
    """Create default theme JSON files if they don't exist."""
    dark_theme_path = os.path.join(THEMES_FOLDER, "dark_theme.json")
    if not os.path.exists(dark_theme_path):
        default_dark_theme = {
            "name": "Dark Theme",
            "colors": {
                "WindowBg": [25, 25, 25, 255],
                "FrameBg": [35, 35, 35, 255],
                "Button": [60, 70, 60, 255],
                "ButtonHovered": [80, 120, 80, 255],
                "ButtonActive": [100, 150, 100, 255],
                "Text": [220, 220, 220, 255],
                "SliderGrab": [100, 150, 100, 255],
                "SliderGrabActive": [120, 180, 120, 255],
                "Header": [40, 40, 40, 255],
                "ScrollbarBg": [35, 35, 35, 128],
                "ScrollbarGrab": [60, 70, 60, 255],
                "ScrollbarGrabHovered": [80, 120, 80, 255],
                "ScrollbarGrabActive": [100, 150, 100, 255],
                "CheckMark": [100, 150, 100, 255],
                "HeaderHovered": [80, 120, 80, 255],
                "HeaderActive": [100, 150, 100, 255],
                "Tab": [60, 70, 60, 255],
                "TabHovered": [80, 120, 80, 255],
                "TabActive": [100, 150, 100, 255],
                "TitleBg": [25, 25, 25, 255],
                "TitleBgActive": [40, 50, 40, 255],
                "TitleBgCollapsed": [25, 25, 25, 128],
                "MenuBarBg": [30, 30, 30, 255],
                "Border": [70, 90, 70, 255],
                "Separator": [70, 90, 70, 255],
                "PopupBg": [35, 35, 35, 240],
                "TextSelectedBg": [80, 120, 80, 150]
            },
            "styles": {
                "FrameRounding": 8.0,
                "FrameBorderSize": 0.5,
                "WindowRounding": 12.0,
                "ScrollbarSize": 12.0,
                "ScrollbarRounding": 8.0,
                "TabRounding": 8.0,
                "GrabRounding": 8.0,
                "ChildRounding": 8.0,
                "PopupRounding": 8.0,
                "ItemSpacing": [8, 6],
                "ItemInnerSpacing": [6, 6]
            }
        }
        with open(dark_theme_path, 'w', encoding='utf-8') as f:
            json.dump(default_dark_theme, f, indent=4)
        logging.info(f"Created default dark theme file: {dark_theme_path}")

    light_theme_path = os.path.join(THEMES_FOLDER, "light_theme.json")
    if not os.path.exists(light_theme_path):
        default_light_theme = {
            "name": "Light Theme",
            "colors": {
                "WindowBg": [248, 250, 252, 255],
                "FrameBg": [235, 242, 248, 255],
                "Button": [200, 230, 230, 255],
                "ButtonHovered": [150, 210, 210, 255],
                "ButtonActive": [100, 190, 190, 255],
                "Text": [40, 50, 60, 255],
                "SliderGrab": [80, 180, 180, 255],
                "SliderGrabActive": [60, 160, 160, 255],
                "Header": [220, 240, 240, 255],
                "ScrollbarBg": [235, 242, 248, 128],
                "ScrollbarGrab": [180, 220, 220, 255],
                "ScrollbarGrabHovered": [150, 210, 210, 255],
                "ScrollbarGrabActive": [100, 190, 190, 255],
                "CheckMark": [80, 180, 180, 255],
                "HeaderHovered": [180, 220, 220, 255],
                "HeaderActive": [150, 210, 210, 255],
                "Tab": [200, 230, 230, 255],
                "TabHovered": [150, 210, 210, 255],
                "TabActive": [100, 190, 190, 255],
                "TitleBg": [235, 242, 248, 255],
                "TitleBgActive": [220, 240, 240, 255],
                "TitleBgCollapsed": [235, 242, 248, 128],
                "MenuBarBg": [220, 240, 240, 255],
                "Border": [180, 220, 220, 255],
                "Separator": [180, 220, 220, 255],
                "PopupBg": [248, 250, 252, 240],
                "TextSelectedBg": [150, 210, 210, 150]
            },
            "styles": {
                "FrameRounding": 8.0,
                "FrameBorderSize": 0.5,
                "WindowRounding": 12.0,
                "ScrollbarSize": 12.0,
                "ScrollbarRounding": 8.0,
                "TabRounding": 8.0,
                "GrabRounding": 8.0,
                "ChildRounding": 8.0,
                "PopupRounding": 8.0,
                "ItemSpacing": [8, 6],
                "ItemInnerSpacing": [6, 6]
            }
        }
        with open(light_theme_path, 'w', encoding='utf-8') as f:
            json.dump(default_light_theme, f, indent=4)
        logging.info(f"Created default light theme file: {light_theme_path}")

    demo_theme_path = os.path.join(THEMES_FOLDER, "demo_theme.json.demo")
    if not os.path.exists(demo_theme_path):
        demo_theme = {
            "name": "Demo Theme",
            "colors": {
                "WindowBg": [18, 24, 34, 255],
                "FrameBg": [30, 40, 56, 255],
                "Button": [40, 90, 160, 255],
                "ButtonHovered": [55, 120, 200, 255],
                "ButtonActive": [35, 95, 170, 255],
                "Text": [220, 230, 245, 255],
                "SliderGrab": [70, 140, 220, 255],
                "SliderGrabActive": [90, 160, 240, 255],
                "Header": [35, 50, 75, 255],
                "ScrollbarBg": [18, 24, 34, 180],
                "ScrollbarGrab": [60, 120, 190, 255],
                "ScrollbarGrabHovered": [80, 150, 220, 255],
                "ScrollbarGrabActive": [55, 110, 180, 255],
                "CheckMark": [100, 160, 240, 255],
                "HeaderHovered": [55, 120, 200, 255],
                "HeaderActive": [40, 90, 160, 255],
                "Tab": [30, 40, 56, 255],
                "TabHovered": [55, 120, 200, 255],
                "TabActive": [40, 90, 160, 255],
                "TitleBg": [22, 28, 40, 255],
                "TitleBgActive": [30, 40, 56, 255],
                "TitleBgCollapsed": [22, 28, 40, 180],
                "MenuBarBg": [25, 32, 48, 255],
                "Border": [45, 60, 95, 255],
                "Separator": [45, 60, 95, 255],
                "PopupBg": [20, 26, 38, 245],
                "TextSelectedBg": [55, 120, 200, 150]
            },
            "styles": {
                "FrameRounding": 8.0,
                "FrameBorderSize": 0.5,
                "WindowRounding": 12.0,
                "ScrollbarSize": 12.0,
                "ScrollbarRounding": 8.0,
                "TabRounding": 8.0,
                "GrabRounding": 8.0,
                "ChildRounding": 8.0,
                "PopupRounding": 8.0,
                "ItemSpacing": [8, 6],
                "ItemInnerSpacing": [6, 6]
            }
        }
        with open(demo_theme_path, 'w', encoding='utf-8') as f:
            json.dump(demo_theme, f, indent=4)
        logging.info(f"Created demo theme file: {demo_theme_path}")


def load_all_themes() -> None:
    """Discover and cache all available themes."""
    global AVAILABLE_THEMES
    try:
        AVAILABLE_THEMES = discover_themes()
        for theme_name, theme_info in AVAILABLE_THEMES.items():
            if load_theme_from_file(theme_name):
                logging.info(f"Discovered theme: {theme_info.get('display_name', theme_name)} ({theme_name})")
    except Exception as e:
        logging.error(f"Error in load_all_themes: {e}")
        import traceback
        logging.error(traceback.format_exc())


def create_theme(theme_name: str) -> None:
    """Discover a theme (no-op for framework-agnostic - themes are loaded on demand)."""
    load_all_themes()


def apply_theme(theme_tag: str) -> None:
    """
    Apply the specified theme to the GUI.
    Delegates to the registered theme applier (from GUI module).
    """
    if _theme_applier:
        _theme_applier(theme_tag)
    else:
        logging.debug(f"Theme applier not registered; storing preference: {theme_tag}")


def get_theme_dropdown_items() -> list:
    """Get list of theme display names for dropdown."""
    items = []
    for theme_name, theme_info in AVAILABLE_THEMES.items():
        display_name = theme_info.get("display_name") or theme_name.replace('_', ' ').title()
        theme_info["display_name"] = display_name
        items.append(display_name)
    return items


def get_theme_name_from_display(display_name: str) -> str:
    """Get theme name from display name."""
    if display_name is None or (isinstance(display_name, str) and display_name.strip() == ""):
        if AVAILABLE_THEMES:
            return list(AVAILABLE_THEMES.keys())[0]
        return "dark_theme"

    for theme_name, theme_info in AVAILABLE_THEMES.items():
        theme_display = theme_info.get("display_name") or theme_name.replace('_', ' ').title()
        theme_info["display_name"] = theme_display
        if theme_display == display_name:
            return theme_name

    if AVAILABLE_THEMES:
        return list(AVAILABLE_THEMES.keys())[0]
    return "dark_theme"


def get_available_themes() -> dict:
    """Get the dictionary of available themes."""
    return AVAILABLE_THEMES


def get_current_theme() -> str:
    """Get the current theme name."""
    return CURRENT_THEME


def set_current_theme(theme_name: str) -> None:
    """Set the current theme name."""
    global CURRENT_THEME
    if theme_name is None or (isinstance(theme_name, str) and theme_name.strip() == ""):
        CURRENT_THEME = "dark_theme"
    else:
        CURRENT_THEME = theme_name


def unload_all_themes() -> None:
    """Clear the themes registry so themes can be reloaded from disk."""
    global AVAILABLE_THEMES
    AVAILABLE_THEMES.clear()
    logging.info("Cleared AVAILABLE_THEMES registry")
