# Theme Documentation

This guide explains how to create custom themes for LYTE.

## Quick Start

Save the theme file in the themes folder:

- **Portable installation:** `themes\` (relative to application directory)
- **Exe installation:** `%LOCALAPPDATA%\LYTE\themes\`

## How Themes Work

LYTE uses a **PySide6 (Qt)**-based interface. Theme colors and styles from your JSON file are converted to Qt stylesheets (QSS) and applied to the application. The JSON structure has not changed—all color names, style properties, and values remain compatible. Themes are applied when you select them from the View → Theme menu, and they hot-reload when you edit theme files while LYTE is running.

## Basic Structure

A theme file is a JSON file with the following structure:

```json
{
    "name": "Your Theme Name",
    "colors": {
        "Element1Name": [R, G, B, A],
        "Element2Name": [R, G, B, A]
    },
    "styles": {
        "Element1Name": Value,
        "Element2Name": Value
    }
}
```

## File Naming

- See `demo_theme.json.demo` for a complete example (rename it to `.json` to use it)
- Example: `ocean_theme.json` creates a theme named `ocean_theme`
- The filename (without `.json`) becomes the theme identifier
- Theme files must end with `.json` (e.g., `my_theme.json`)
- Use **View → Reload themes** to add new themes without restarting, or restart LYTE—your theme will appear in the theme dropdown menu

## Theme Folder Location

Theme files are stored in the `themes` folder:

- **Portable installation:** `themes\` (relative to application directory)
- **Exe installation:** `%LOCALAPPDATA%\LYTE\themes\`

Note: `%LOCALAPPDATA%` typically expands to `C:\Users\<username>\AppData\Local\` on Windows.

## Color Values

All colors are in RGBA format: `[Red, Green, Blue, Alpha]`

- Example: `[255, 0, 0, 255]` = solid red, `[255, 0, 0, 128]` = semi-transparent red
- Alpha controls transparency: 255 = fully opaque, 0 = fully transparent
- Each value ranges from 0–255

## Available Colors

All color properties available in LYTE themes. Colors are applied to different UI elements in the **PySide6/Qt interface** via stylesheets.

| Color Name | Description |
| --- | --- |
| `WindowBg` | Background color for all windows and main panels. This is the base background color of the application. |
| `FrameBg` | Background color for frames, input fields, text boxes, and container elements. Usually slightly lighter or darker than WindowBg for contrast. |
| `Button` | Default button background color when not hovered or active. This is the base state for all buttons. |
| `ButtonHovered` | Button background color when the mouse cursor hovers over it. Typically brighter or more saturated than the default Button color. |
| `ButtonActive` | Button background color when clicked or pressed. Usually the brightest or most saturated state to provide clear feedback. |
| `Text` | Default text color used throughout the interface for labels, text inputs, and general UI text. Ensure good contrast with background colors. |
| `SliderGrab` | Color of the slider handle/thumb (the draggable part of sliders). Used for volume and progress sliders. |
| `SliderGrabActive` | Color of the slider handle when it's being actively dragged. Usually brighter than SliderGrab to indicate interaction. |
| `Header` | Background color for collapsible headers, list headers, and section headers. Used in expandable UI sections. |
| `HeaderHovered` | Header background color when the mouse hovers over it. Provides visual feedback for interactive headers. |
| `HeaderActive` | Header background color when clicked or expanded. Indicates the active/expanded state of collapsible sections. |
| `ScrollbarBg` | Background color of the scrollbar track (the area behind the scrollbar handle). Usually semi-transparent (alpha < 255) for a subtle appearance. |
| `ScrollbarGrab` | Color of the scrollbar handle/thumb (the draggable part). Should contrast with ScrollbarBg for visibility. |
| `ScrollbarGrabHovered` | Scrollbar handle color when the mouse hovers over it. Provides hover feedback for better interactivity. |
| `ScrollbarGrabActive` | Scrollbar handle color when being actively dragged. Usually the brightest state to indicate active interaction. |
| `CheckMark` | Color of checkmarks in checkboxes. Should contrast well with the checkbox background for visibility. |
| `Tab` | Background color of inactive tabs. Used in tabbed interfaces to distinguish inactive tabs from the active one. |
| `TabHovered` | Tab background color when the mouse hovers over it. Provides visual feedback before clicking. |
| `TabActive` | Background color of the currently active/selected tab. Should stand out from inactive tabs to clearly show the active state. |
| `TitleBg` | Background color of window title bars. The area at the top of windows that typically contains the window title. |
| `TitleBgActive` | Background color of the active/focused window title bar. Used to indicate which window has focus when multiple windows are open. |
| `TitleBgCollapsed` | Background color of collapsed window title bars. Usually semi-transparent (alpha < 255) for a subtle appearance when windows are minimized or collapsed. |
| `MenuBarBg` | Background color of the menu bar at the top of windows. The area containing File, View, Help, etc. menus. |
| `Border` | Color of borders around frames, windows, and UI elements. Used to create visual separation between different sections. |
| `Separator` | Color of separator lines between UI elements. Used for visual division in menus, lists, and grouped controls. |
| `PopupBg` | Background color of popup menus, dropdown menus, and dialog boxes. Usually slightly transparent (alpha around 240–250) for a layered appearance. |
| `TextSelectedBg` | Background color behind selected text. Used when text is highlighted/selected. Usually semi-transparent (alpha around 150–200) so text remains readable. |

## Style Values

Style properties control the appearance and spacing of UI elements. These values affect the visual style rather than colors. They are mapped to Qt stylesheet properties (e.g., border-radius, padding).

| Style Name | Description |
| --- | --- |
| `FrameRounding` | Corner rounding radius for frames, input fields, and containers. Value in pixels: 0.0 = sharp corners, higher values = more rounded. Typical range: 0–12. |
| `FrameBorderSize` | Thickness of borders around frames and input fields in pixels. 0.0 = no border, higher values = thicker borders. Typical range: 0.0–2.0. |
| `WindowRounding` | Corner rounding radius for windows in pixels. 0.0 = sharp corners, higher values = more rounded. Usually equal to or greater than FrameRounding. Typical range: 0–16. |
| `ScrollbarSize` | Width of scrollbars in pixels. Controls how wide the scrollbar track appears. Typical range: 8–20 pixels. |
| `ScrollbarRounding` | Corner rounding radius for scrollbars in pixels. Makes scrollbar handles rounded. 0.0 = sharp, higher = more rounded. Typical range: 0–8. |
| `TabRounding` | Corner rounding radius for tabs in pixels. Controls how rounded tab corners are. 0.0 = sharp, higher = more rounded. Typical range: 0–8. |
| `GrabRounding` | Corner rounding radius for grab handles (slider thumbs, resize handles) in pixels. Makes interactive handles rounded. Typical range: 0–8. |
| `ChildRounding` | Corner rounding radius for child windows and panels in pixels. Controls rounding of nested UI containers. Typical range: 0–12. |
| `PopupRounding` | Corner rounding radius for popup menus and dialogs in pixels. Makes popups and dropdowns rounded. Typical range: 0–12. |
| `ItemSpacing` | Spacing between UI items as an array: `[horizontal, vertical]` in pixels. Controls spacing between buttons, inputs, and other elements. Example: `[8, 6]` = 8px horizontal, 6px vertical. |
| `ItemInnerSpacing` | Inner spacing within items (padding inside buttons, inputs, etc.) as an array: `[horizontal, vertical]` in pixels. Controls internal padding. Example: `[6, 6]` = 6px padding on all sides. |

## Tips

- Higher rounding values (8–12) create softer, more rounded corners
- Rounding values of 0.0 create sharp, modern corners
- Alpha values (transparency) work best for backgrounds, not text
- Keep contrast ratios high for text readability
- Test your theme with both light and dark content to ensure readability
- Use a color picker tool to get RGB values from images or websites
- Use **View → Reload themes** to refresh themes after editing without restarting LYTE

## Example Theme File

```json
{
  "name": "Demo Theme",
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
    "HeaderHovered": [80, 120, 80, 255],
    "HeaderActive": [100, 150, 100, 255],
    "ScrollbarBg": [35, 35, 35, 128],
    "ScrollbarGrab": [60, 70, 60, 255],
    "ScrollbarGrabHovered": [80, 120, 80, 255],
    "ScrollbarGrabActive": [100, 150, 100, 255],
    "CheckMark": [100, 150, 100, 255],
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
    "FrameRounding": 8,
    "FrameBorderSize": 0.5,
    "WindowRounding": 12,
    "ScrollbarSize": 12,
    "ScrollbarRounding": 8,
    "TabRounding": 8,
    "GrabRounding": 8,
    "ChildRounding": 8,
    "PopupRounding": 8,
    "ItemSpacing": [8, 6],
    "ItemInnerSpacing": [6, 6]
  }
}
```
