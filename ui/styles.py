from tkinter import ttk
import tkinter as tk

def apply_styles(root):
    """Apply custom dark mode styles to the application"""
    style = ttk.Style()

    # Tokyo Night inspired color palette
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
        'text_secondary': '#565f89',  # Secondary text color
        'success': '#9ece6a',        # Green for success states
        'error': '#f7768e'           # Red for error states
    }

    # Configure main window
    root.configure(bg=colors['bg_darker'])

    # Header styling
    style.configure(
        "Header.TLabel",
        background=colors['bg_darker'],
        foreground=colors['primary'],
        font=("Segoe UI", 24, "bold"),
        padding=(0, 20)
    )

    # Modern Frame styling
    style.configure(
        "Modern.TFrame",
        background=colors['bg_darker']
    )

    # Server list styling
    style.configure(
        "ServerItem.TFrame",
        background=colors['bg_lighter'],
        relief="solid",
        borderwidth=1
    )

    style.configure(
        "ServerInfo.TFrame",
        background=colors['bg_lighter']
    )

    # Server list elements
    style.configure(
        "Server.TCheckbutton",
        background=colors['bg_lighter'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.map(
        "Server.TCheckbutton",
        background=[("active", colors['bg_lighter'])],
        foreground=[("active", colors['primary'])]
    )

    style.configure(
        "ServerName.TLabel",
        background=colors['bg_lighter'],
        foreground=colors['text'],
        font=("Segoe UI", 12, "bold")
    )

    style.configure(
        "ServerDetails.TLabel",
        background=colors['bg_lighter'],
        foreground=colors['text_secondary'],
        font=("Segoe UI", 10)
    )

    # LabelFrame styling
    style.configure(
        "Modern.TLabelframe",
        background=colors['bg_darker'],
        foreground=colors['text'],
        borderwidth=2,
        relief="solid"
    )

    style.configure(
        "Modern.TLabelframe.Label",
        background=colors['bg_darker'],
        foreground=colors['primary'],
        font=("Segoe UI", 12, "bold"),
        padding=(15, 5)
    )

    # Drop zone styling
    style.configure(
        "DropZone.TLabel",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=25,
        relief="solid",
        borderwidth=2
    )

    style.configure(
        "DropZoneHover.TLabel",
        background=colors['hover'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=25,
        relief="solid",
        borderwidth=2
    )

    style.configure(
        "DropZoneActive.TLabel",
        background=colors['active'],
        foreground=colors['bg_dark'],
        font=("Segoe UI", 11),
        padding=25,
        relief="solid",
        borderwidth=2
    )

    # Modern button styling
    style.configure(
        "Accent.TButton",
        background=colors['primary'],
        foreground=colors['text'],
        font=("Segoe UI", 10, "bold"),
        padding=(25, 12),
        relief="flat"
    )

    style.map(
        "Accent.TButton",
        background=[("active", colors['hover'])],
        foreground=[("active", colors['text'])],
        relief=[("active", "flat")]
    )

    # Configure text widget colors
    root.option_add("*Text.background", colors['bg_dark'])
    root.option_add("*Text.foreground", colors['text'])
    root.option_add("*Text.selectBackground", colors['primary'])
    root.option_add("*Text.selectForeground", colors['bg_dark'])
    root.option_add("*Text.insertBackground", colors['text'])
    root.option_add("*Text.font", ("Consolas", 11))