# Theme Documentation

This guide explains how to create custom themes for LYTE.

## Quick Start

Save the theme file in the themes folder:

- **Portable installation:** `themes\` (relative to application directory)
- **Exe installation:** `%LOCALAPPDATA%\LYTE\themes\`

## How Themes Work

LYTE uses a **PySide6 (Qt)**-based interface with two theme formats:

1. **JSON themes** — Colors and styles are converted to Qt stylesheets (QSS). Use the structured format below.
2. **QSS themes** — Raw Qt Style Sheet (CSS-like) files for full control. See [Custom QSS Themes](#custom-qss-themes) below.

Themes are applied when you select them from the View → Theme menu and hot-reload when you edit theme files while LYTE is running.

## Custom QSS Themes

You can create themes using raw **Qt Style Sheets (QSS)**, which use CSS-like syntax. This gives you full control over every widget's appearance.

### Creating a QSS Theme

1. Copy `custom_theme.qss.example` from the themes folder to a new file (e.g., `ocean.qss`, `midnight.qss`).
2. Edit the file with your colors, borders, and styles.
3. Save in the themes folder. The theme appears in View → Theme.
4. Use **View → Reload themes** to pick up new or edited QSS files.

### QSS Syntax

QSS is similar to CSS. Use selectors like `QPushButton`, `QLineEdit`, and pseudo-states like `:hover`, `:pressed`, `:disabled`:

```css
QPushButton {
    background-color: #3c463c;
    color: #dcdcdc;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #507850;
}
```

### Widget Selectors

| Selector | Description |
| --- | --- |
| `QWidget`, `QMainWindow`, `QDialog` | Base backgrounds |
| `QPushButton`, `:hover`, `:pressed`, `:disabled` | Buttons |
| `QLineEdit`, `QPlainTextEdit`, `QSpinBox`, `QComboBox` | Inputs |
| `QSlider::groove:horizontal`, `QSlider::handle:horizontal` | Sliders |
| `QMenuBar`, `QMenu`, `QMenu::item:selected` | Menus |
| `QListWidget`, `QListWidget::item:selected` | Lists |
| `QCheckBox`, `QCheckBox::indicator` | Checkboxes |
| `QScrollBar:vertical`, `QScrollBar::handle:vertical` | Scrollbars |
| `QGroupBox`, `QToolTip` | Groups and tooltips |

### File Naming for QSS

- `my_theme.qss` → theme appears as "My Theme"
- Filename (without `.qss`) becomes the theme identifier
- Template: `custom_theme.qss.example` (copy and rename to use)
- **Showcase:** `aurora_theme.qss` is included as a dramatic example—select "Aurora Theme" from View → Theme to see gradients, rounded corners, and a full purple/cyan palette

## Basic Structure (JSON Themes)

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
| `MenuBarBg` | Background color of the menu bar at the top of windows. The area containing File, View, Moderation, Help, etc. menus. |
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

## Example Theme File (JSON)

The `demo_theme.json.demo` file uses a blue/ocean palette. Rename it to `.json` to use it:

```json
{
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
    "HeaderHovered": [55, 120, 200, 255],
    "HeaderActive": [40, 90, 160, 255],
    "ScrollbarBg": [18, 24, 34, 180],
    "ScrollbarGrab": [60, 120, 190, 255],
    "ScrollbarGrabHovered": [80, 150, 220, 255],
    "ScrollbarGrabActive": [55, 110, 180, 255],
    "CheckMark": [100, 160, 240, 255],
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
