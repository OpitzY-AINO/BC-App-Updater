from tkinter import ttk
import tkinter as tk

def apply_styles(root):
    """Apply custom dark mode styles to the application"""
    style = ttk.Style()

    # Modern dark color palette
    colors = {
        'bg_dark': '#1a1b26',         # Dark background
        'bg_darker': '#16161e',       # Darker background for contrast
        'bg_lighter': '#24283b',      # Slightly lighter background for elements
        'primary': '#7aa2f7',         # Modern blue accent
        'secondary': '#bb9af7',       # Purple accent
        'hover': '#3d59a1',          # Darker blue for hover
        'active': '#2ac3de',         # Cyan for active states
        'border': '#414868',         # Border color
        'text': '#c0caf5',           # Main text color
        'text_secondary': '#565f89'   # Secondary text color
    }

    # Configure main window
    root.configure(bg=colors['bg_dark'])

    # Configure frame styles
    style.configure(
        "TFrame",
        background=colors['bg_dark']
    )

    style.configure(
        "Card.TFrame",
        background=colors['bg_lighter'],
        borderwidth=1,
        relief="solid"
    )

    # Configure modern labelframe
    style.configure(
        "TLabelframe",
        background=colors['bg_dark'],
        borderwidth=1,
        relief="solid"
    )

    style.configure(
        "TLabelframe.Label",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 11, "bold"),
        padding=(10, 5)
    )

    # Configure drop zone styles with modern look
    style.configure(
        "DropZone.TLabel",
        background=colors['bg_lighter'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['border']
    )

    style.configure(
        "DropZoneHover.TLabel",
        background=colors['hover'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['primary']
    )

    style.configure(
        "DropZoneActive.TLabel",
        background=colors['active'],
        foreground=colors['bg_dark'],
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['primary']
    )

    # Configure modern button style
    style.configure(
        "Accent.TButton",
        background=colors['primary'],
        foreground=colors['text'],
        font=("Segoe UI", 10, "bold"),
        padding=(20, 10),
        borderwidth=0
    )

    style.map(
        "Accent.TButton",
        background=[("active", colors['hover'])],
        foreground=[("active", colors['text'])]
    )

    # Configure checkbox styles
    style.configure(
        "TCheckbutton",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.map(
        "TCheckbutton",
        background=[("active", colors['bg_dark'])],
        foreground=[("active", colors['primary'])]
    )

    # Configure label styles
    style.configure(
        "TLabel",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.configure(
        "Header.TLabel",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 16, "bold"),
        padding=(0, 10)
    )

    # Configure canvas and scrollbar for server list
    style.configure(
        "ServerList.TFrame",
        background=colors['bg_lighter'],
        relief="solid",
        borderwidth=1
    )

    # Configure text area
    root.option_add("*Text.background", colors['bg_lighter'])
    root.option_add("*Text.foreground", colors['text'])
    root.option_add("*Text.selectBackground", colors['primary'])
    root.option_add("*Text.selectForeground", colors['bg_dark'])
    root.option_add("*Text.insertBackground", colors['text'])  # Cursor color