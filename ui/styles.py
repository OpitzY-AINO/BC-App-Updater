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

    # Configure frame styles
    style.configure(
        "TFrame",
        background=colors['bg_darker']
    )

    # Server list specific styles
    style.configure(
        "ServerList.TFrame",
        background=colors['bg_lighter'],
        relief="solid",
        borderwidth=2
    )

    # Configure checkbox and label styles for server list
    style.configure(
        "TCheckbutton",
        background=colors['bg_lighter'],
        foreground=colors['text'],
        font=("Segoe UI", 10),
        padding=(5, 5)
    )

    style.map(
        "TCheckbutton",
        background=[("active", colors['bg_lighter'])],
        foreground=[("active", colors['primary'])]
    )

    style.configure(
        "TLabel",
        background=colors['bg_lighter'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    # Configure main window
    root.configure(bg=colors['bg_darker'])


    style.configure(
        "Card.TFrame",
        background=colors['bg_lighter'],
        borderwidth=1,
        relief="solid"
    )

    # Configure modern labelframe with rounded corners look
    style.configure(
        "TLabelframe",
        background=colors['bg_darker'],
        borderwidth=2,
        relief="solid"
    )

    style.configure(
        "TLabelframe.Label",
        background=colors['bg_darker'],
        foreground=colors['primary'],
        font=("Segoe UI", 12, "bold"),
        padding=(15, 8)
    )

    # Configure drop zone styles with modern look
    style.configure(
        "DropZone.TLabel",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=25,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['border']
    )

    style.configure(
        "DropZoneHover.TLabel",
        background=colors['hover'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=25,
        relief="solid",
        borderwidth=2,
        bordercolor=colors['primary']
    )

    style.configure(
        "DropZoneActive.TLabel",
        background=colors['active'],
        foreground=colors['bg_dark'],
        font=("Segoe UI", 11),
        padding=25,
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
        padding=(25, 12),
        borderwidth=0,
        relief="flat"
    )

    style.map(
        "Accent.TButton",
        background=[("active", colors['hover'])],
        foreground=[("active", colors['text'])]
    )


    # Configure Header label styles
    style.configure(
        "Header.TLabel",
        background=colors['bg_darker'],
        foreground=colors['primary'],
        font=("Segoe UI", 24, "bold"),
        padding=(0, 15)
    )

    # Configure text area
    root.option_add("*Text.background", colors['bg_dark'])
    root.option_add("*Text.foreground", colors['text'])
    root.option_add("*Text.selectBackground", colors['primary'])
    root.option_add("*Text.selectForeground", colors['bg_dark'])
    root.option_add("*Text.insertBackground", colors['text'])
    root.option_add("*Text.font", ("Consolas", 11))