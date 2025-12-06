# =============================================================================
# THEME MANAGEMENT FUNCTIONS
# =============================================================================

# Standard Library Imports
import json
import logging
import os
import sys

# Third-Party Imports
from dearpygui.dearpygui import (
    add_theme_color,
    add_theme_style,
    bind_theme,
    configure_item,
    does_item_exist,
    theme,
    theme_component,
    mvAll,
    mvThemeCol_WindowBg,
    mvThemeCol_FrameBg,
    mvThemeCol_Button,
    mvThemeCol_ButtonHovered,
    mvThemeCol_ButtonActive,
    mvThemeCol_Text,
    mvThemeCol_SliderGrab,
    mvThemeCol_SliderGrabActive,
    mvThemeCol_Header,
    mvThemeCol_ScrollbarBg,
    mvThemeCol_ScrollbarGrab,
    mvThemeCol_ScrollbarGrabHovered,
    mvThemeCol_ScrollbarGrabActive,
    mvThemeCol_CheckMark,
    mvThemeCol_HeaderHovered,
    mvThemeCol_HeaderActive,
    mvThemeCol_Tab,
    mvThemeCol_TabHovered,
    mvThemeCol_TabActive,
    mvThemeCol_TitleBg,
    mvThemeCol_TitleBgActive,
    mvThemeCol_TitleBgCollapsed,
    mvThemeCol_MenuBarBg,
    mvThemeCol_Border,
    mvThemeCol_Separator,
    mvThemeCol_PopupBg,
    mvThemeCol_TextSelectedBg,
    mvStyleVar_FrameRounding,
    mvStyleVar_FrameBorderSize,
    mvStyleVar_WindowRounding,
    mvStyleVar_ScrollbarSize,
    mvStyleVar_ScrollbarRounding,
    mvStyleVar_TabRounding,
    mvStyleVar_GrabRounding,
    mvStyleVar_ChildRounding,
    mvStyleVar_PopupRounding,
    mvStyleVar_ItemSpacing,
    mvStyleVar_ItemInnerSpacing,
)

# =============================================================================

# Theme constant mapping for loading from JSON
THEME_COLOR_MAP = {
    "WindowBg": mvThemeCol_WindowBg,
    "FrameBg": mvThemeCol_FrameBg,
    "Button": mvThemeCol_Button,
    "ButtonHovered": mvThemeCol_ButtonHovered,
    "ButtonActive": mvThemeCol_ButtonActive,
    "Text": mvThemeCol_Text,
    "SliderGrab": mvThemeCol_SliderGrab,
    "SliderGrabActive": mvThemeCol_SliderGrabActive,
    "Header": mvThemeCol_Header,
    "ScrollbarBg": mvThemeCol_ScrollbarBg,
    "ScrollbarGrab": mvThemeCol_ScrollbarGrab,
    "ScrollbarGrabHovered": mvThemeCol_ScrollbarGrabHovered,
    "ScrollbarGrabActive": mvThemeCol_ScrollbarGrabActive,
    "CheckMark": mvThemeCol_CheckMark,
    "HeaderHovered": mvThemeCol_HeaderHovered,
    "HeaderActive": mvThemeCol_HeaderActive,
    "Tab": mvThemeCol_Tab,
    "TabHovered": mvThemeCol_TabHovered,
    "TabActive": mvThemeCol_TabActive,
    "TitleBg": mvThemeCol_TitleBg,
    "TitleBgActive": mvThemeCol_TitleBgActive,
    "TitleBgCollapsed": mvThemeCol_TitleBgCollapsed,
    "MenuBarBg": mvThemeCol_MenuBarBg,
    "Border": mvThemeCol_Border,
    "Separator": mvThemeCol_Separator,
    "PopupBg": mvThemeCol_PopupBg,
    "TextSelectedBg": mvThemeCol_TextSelectedBg,
}

THEME_STYLE_MAP = {
    "FrameRounding": mvStyleVar_FrameRounding,
    "FrameBorderSize": mvStyleVar_FrameBorderSize,
    "WindowRounding": mvStyleVar_WindowRounding,
    "ScrollbarSize": mvStyleVar_ScrollbarSize,
    "ScrollbarRounding": mvStyleVar_ScrollbarRounding,
    "TabRounding": mvStyleVar_TabRounding,
    "GrabRounding": mvStyleVar_GrabRounding,
    "ChildRounding": mvStyleVar_ChildRounding,
    "PopupRounding": mvStyleVar_PopupRounding,
    "ItemSpacing": mvStyleVar_ItemSpacing,
    "ItemInnerSpacing": mvStyleVar_ItemInnerSpacing,
}

# Global theme state (will be initialized by init_theme_system)
AVAILABLE_THEMES: dict = {}
CURRENT_THEME: str = "dark_theme"
THEMES_FOLDER: str = ""

def init_theme_system(themes_folder: str) -> None:
    """
    Initialize the theme system with the themes folder path.
    
    Args:
        themes_folder: Path to the themes directory
    """
    global THEMES_FOLDER
    THEMES_FOLDER = themes_folder
    os.makedirs(THEMES_FOLDER, exist_ok=True)

def discover_themes() -> dict:
    """
    Scan the themes folder and discover all available theme files.
    Checks both PyInstaller bundle location and user app folder.
    
    Returns:
        dict: Dictionary mapping theme names to theme info {"theme_name": {"file": "file.json", "display_name": "Name"}}
    """
    themes = {}
    
    # Check PyInstaller bundle location first (for bundled themes)
    bundle_themes_folder = None
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_themes_folder = os.path.join(sys._MEIPASS, 'themes')
        if os.path.exists(bundle_themes_folder):
            try:
                for filename in os.listdir(bundle_themes_folder):
                    if filename.endswith('.json'):
                        theme_name = filename[:-5]  # Remove .json extension
                        theme_path = os.path.join(bundle_themes_folder, filename)
                        
                        try:
                            with open(theme_path, 'r', encoding='utf-8') as f:
                                theme_data = json.load(f)
                            
                            # Get display name from theme data, or use filename as fallback
                            display_name = theme_data.get('name', theme_name.replace('_', ' ').title())
                            
                            themes[theme_name] = {
                                "file": filename,
                                "display_name": display_name,
                                "bundle_path": theme_path  # Store bundle path for loading
                            }
                        except (json.JSONDecodeError, IOError) as e:
                            logging.warning(f"Failed to load bundled theme {filename}: {e}")
                            continue
            except Exception as e:
                logging.warning(f"Error scanning bundled themes folder: {e}")
    
    # Check user app folder (for custom themes - these override bundled themes)
    if THEMES_FOLDER and os.path.exists(THEMES_FOLDER):
        try:
            for filename in os.listdir(THEMES_FOLDER):
                if filename.endswith('.json'):
                    theme_name = filename[:-5]  # Remove .json extension
                    theme_path = os.path.join(THEMES_FOLDER, filename)
                    
                    try:
                        with open(theme_path, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                        
                        # Get display name from theme data, or use filename as fallback
                        display_name = theme_data.get('name', theme_name.replace('_', ' ').title())
                        
                        # User themes override bundled themes
                        themes[theme_name] = {
                            "file": filename,
                            "display_name": display_name,
                            "user_path": theme_path  # Store user path for loading
                        }
                    except (json.JSONDecodeError, IOError) as e:
                        logging.warning(f"Failed to load theme {filename}: {e}")
                        continue
        except Exception as e:
            logging.warning(f"Error scanning themes folder: {e}")
    
    return themes

def load_theme_from_file(theme_name: str) -> dict:
    """
    Load theme configuration from a JSON file.
    Checks user folder first, then PyInstaller bundle location.
    
    Args:
        theme_name: Name of the theme file (without .json extension)
        
    Returns:
        dict: Theme configuration with 'colors' and 'styles' keys, or None if file doesn't exist
    """
    # Check user folder first (custom themes override bundled themes)
    if THEMES_FOLDER:
        user_theme_path = os.path.join(THEMES_FOLDER, f"{theme_name}.json")
        if os.path.exists(user_theme_path):
            try:
                with open(user_theme_path, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                return theme_data
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Error loading theme from {user_theme_path}: {e}")
                return None
    
    # Check PyInstaller bundle location
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_theme_path = os.path.join(sys._MEIPASS, 'themes', f"{theme_name}.json")
        if os.path.exists(bundle_theme_path):
            try:
                with open(bundle_theme_path, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                return theme_data
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Error loading bundled theme from {bundle_theme_path}: {e}")
                return None
    
    logging.warning(f"Theme file not found: {theme_name}.json")
    return None

def apply_theme_from_data(theme_tag: str, theme_data: dict) -> None:
    """
    Apply theme data to create a DearPyGui theme.
    
    Args:
        theme_tag: Tag identifier for the theme
        theme_data: Dictionary containing 'colors' and 'styles' keys
    """
    try:
        with theme(tag=theme_tag):
            with theme_component(mvAll):
                # Apply colors
                if 'colors' in theme_data:
                    for color_name, color_value in theme_data['colors'].items():
                        if color_name in THEME_COLOR_MAP:
                            # Convert list/tuple to tuple if needed
                            if isinstance(color_value, list):
                                color_value = tuple(color_value)
                            add_theme_color(THEME_COLOR_MAP[color_name], color_value)
                
                # Apply styles
                if 'styles' in theme_data:
                    for style_name, style_value in theme_data['styles'].items():
                        if style_name in THEME_STYLE_MAP:
                            # Handle styles that take multiple values (like ItemSpacing)
                            if isinstance(style_value, list):
                                add_theme_style(THEME_STYLE_MAP[style_name], *style_value)
                            else:
                                add_theme_style(THEME_STYLE_MAP[style_name], style_value)
    except Exception as e:
        logging.error(f"Error applying theme data for {theme_tag}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        raise

def create_default_theme_files() -> None:
    """Create default theme JSON files if they don't exist."""
    # Default dark theme
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
    
    # Default light theme
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
    
    # Create demo theme file (with .demo extension so it's not detected as a theme)
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
    """Load all discovered themes into DearPyGui."""
    global AVAILABLE_THEMES
    try:
        AVAILABLE_THEMES = discover_themes()
        
        for theme_name, theme_info in AVAILABLE_THEMES.items():
            try:
                theme_data = load_theme_from_file(theme_name)
                if theme_data:
                    apply_theme_from_data(theme_name, theme_data)
                    logging.info(f"Loaded theme: {theme_info['display_name']} ({theme_name})")
                else:
                    logging.warning(f"Failed to load theme: {theme_name}")
            except Exception as e:
                logging.error(f"Error loading theme {theme_name}: {e}")
                import traceback
                logging.error(traceback.format_exc())
    except Exception as e:
        logging.error(f"Error in load_all_themes: {e}")
        import traceback
        logging.error(traceback.format_exc())

def create_theme(theme_name: str) -> None:
    """
    Create and configure a theme for the GUI.
    
    Args:
        theme_name: Name of the theme to create
    """
    # Try to load theme from external file
    theme_data = load_theme_from_file(theme_name)
    
    if theme_data:
        # Apply theme from file
        apply_theme_from_data(theme_name, theme_data)
        display_name = theme_data.get('name', theme_name)
        logging.info(f"Loaded theme '{display_name}' from external file")
    else:
        # Fallback: try to create legacy dark/light themes if they don't exist
        logging.warning(f"Theme '{theme_name}' not found, skipping creation")

def apply_theme(theme_tag: str) -> None:
    """
    Apply the specified theme to the GUI.
    
    Args:
        theme_tag: Theme identifier (theme name)
    """
    bind_theme(theme_tag)

def get_theme_dropdown_items() -> list:
    """
    Get list of theme display names for dropdown.
    
    Returns:
        list: List of theme display names
    """
    items = []
    for theme_name, theme_info in AVAILABLE_THEMES.items():
        display_name = theme_info.get("display_name")
        if not display_name:
            display_name = theme_name.replace('_', ' ').title()
            theme_info["display_name"] = display_name
        items.append(display_name)
    return items

def get_theme_name_from_display(display_name: str) -> str:
    """
    Get theme name from display name.
    
    Args:
        display_name: Display name of the theme
        
    Returns:
        str: Theme name (file identifier), never None
    """
    if display_name is None or (isinstance(display_name, str) and display_name.strip() == ""):
        logging.warning(f"Received invalid display name {display_name!r} when resolving theme; using fallback")
        if AVAILABLE_THEMES:
            return list(AVAILABLE_THEMES.keys())[0]
        return "dark_theme"
    
    for theme_name, theme_info in AVAILABLE_THEMES.items():
        theme_display = theme_info.get("display_name")
        if not theme_display:
            theme_display = theme_name.replace('_', ' ').title()
            theme_info["display_name"] = theme_display
        if theme_display == display_name:
            return theme_name
    # Fallback to first available theme or default
    logging.warning(f"Could not find theme for display name {display_name!r}, using fallback")
    if AVAILABLE_THEMES:
        return list(AVAILABLE_THEMES.keys())[0]
    return "dark_theme"

def get_available_themes() -> dict:
    """
    Get the dictionary of available themes.
    
    Returns:
        dict: Available themes dictionary
    """
    return AVAILABLE_THEMES

def get_current_theme() -> str:
    """
    Get the current theme name.
    
    Returns:
        str: Current theme name
    """
    return CURRENT_THEME

def set_current_theme(theme_name: str) -> None:
    """
    Set the current theme name.
    
    Args:
        theme_name: Name of the theme to set as current
    """
    global CURRENT_THEME
    if theme_name is None:
        logging.warning("set_current_theme received None; falling back to 'dark_theme'")
        CURRENT_THEME = "dark_theme"
    elif isinstance(theme_name, str) and theme_name.strip() == "":
        logging.warning("set_current_theme received empty theme name; falling back to 'dark_theme'")
        CURRENT_THEME = "dark_theme"
    else:
        CURRENT_THEME = theme_name

