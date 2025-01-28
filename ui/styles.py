from tkinter import ttk
import tkinter as tk

def apply_styles(root):
    """Apply custom dark mode styles to the application"""
    style = ttk.Style()

    # Modern dark color palette
    colors = {
        'bg_dark': '#1e1e2e',          # Dark background
        'bg_darker': '#181825',         # Darker shade for contrast
        'primary': '#89b4fa',          # Catppuccin blue
        'secondary': '#a6adc8',        # Subtle gray
        'hover': '#313244',           # Slightly lighter for hover
        'active': '#45475a',          # Even lighter for active states
        'border': '#313244',          # Border color
        'text': '#cdd6f4',            # Light text
        'text_secondary': '#a6adc8',   # Secondary text
        'accent': '#f5c2e7',          # Pink accent
        'error': '#f38ba8',           # Error red
        'success': '#a6e3a1'          # Success green
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
        background=colors['bg_darker'],
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

    # Configure drop zone styles
    style.configure(
        "DropZone.TLabel",
        background=colors['bg_darker'],
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
        foreground=colors['primary'],
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['primary']
    )

    style.configure(
        "DropZoneActive.TLabel",
        background=colors['active'],
        foreground=colors['primary'],
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['primary']
    )

    # Configure modern button styles
    style.configure(
        "Accent.TButton",
        background=colors['primary'],
        foreground=colors['bg_dark'],
        font=("Segoe UI", 10, "bold"),
        padding=(20, 10),
        borderwidth=0
    )

    style.map(
        "Accent.TButton",
        background=[("active", colors['accent'])],
        foreground=[("active", colors['bg_dark'])]
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

    # Configure server list styles
    style.configure(
        "ServerList.TFrame",
        background=colors['bg_darker'],
        relief="solid",
        borderwidth=1
    )

    # Add specific style for server list items
    style.configure(
        "ServerList.TLabel",
        background=colors['bg_darker'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.configure(
        "ServerList.TCheckbutton",
        background=colors['bg_darker'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.map(
        "ServerList.TCheckbutton",
        background=[("active", colors['bg_darker'])],
        foreground=[("active", colors['primary'])]
    )

    # Configure text widget style (used in config input)
    root.option_add("*Text.background", colors['bg_darker'])
    root.option_add("*Text.foreground", colors['text'])
    root.option_add("*Text.selectBackground", colors['primary'])
    root.option_add("*Text.selectForeground", colors['bg_dark'])
    root.option_add("*Text.insertBackground", colors['text'])  # Cursor color

    # Configure canvas background for server list
    root.option_add("*Canvas.background", colors['bg_darker'])
    root.option_add("*Canvas.highlightthickness", 0)

    style.configure(
        "Canvas.TFrame",
        background=colors['bg_dark']
    )