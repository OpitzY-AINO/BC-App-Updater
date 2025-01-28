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
        background=colors['bg_darker']
    )

    # Configure modern labelframe - removed borders
    style.configure(
        "TLabelframe",
        background=colors['bg_dark'],
        borderwidth=0,
        relief="flat"
    )

    style.configure(
        "TLabelframe.Label",
        background=colors['bg_dark'],
        foreground=colors['text'],
        font=("Segoe UI", 11, "bold"),
        padding=(10, 5)
    )

    # Configure drop zone styles - keep subtle border for drag-drop visual feedback
    style.configure(
        "DropZone.TLabel",
        background=colors['bg_darker'],
        foreground=colors['text'],
        font=("Segoe UI", 11),
        padding=20,
        relief="flat",
        borderwidth=0
    )

    style.configure(
        "DropZoneHover.TLabel",
        background=colors['hover'],
        foreground=colors['primary'],
        font=("Segoe UI", 11),
        padding=20,
        relief="flat",
        borderwidth=0
    )

    style.configure(
        "DropZoneActive.TLabel",
        background=colors['active'],
        foreground=colors['primary'],
        font=("Segoe UI", 11),
        padding=20,
        relief="flat",
        borderwidth=0
    )

    # Configure modern button styles with larger size
    style.configure(
        "Accent.TButton",
        background=colors['primary'],
        foreground=colors['bg_dark'],
        font=("Segoe UI", 11, "bold"),  # Increased font size
        padding=(20, 10),  # Increased padding
        relief="flat",
        borderwidth=0,
        width=20  # Increased minimum width for buttons
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

    # Configure Treeview styles - removed borders
    style.configure(
        "ServerList.Treeview",
        background=colors['bg_darker'],
        foreground=colors['text'],
        fieldbackground=colors['bg_darker'],
        borderwidth=0,
        font=("Segoe UI", 10),
        rowheight=30
    )

    style.configure(
        "ServerList.Treeview.Heading",
        background=colors['bg_darker'],
        foreground=colors['text'],
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "ServerList.Treeview",
        background=[
            ("selected", colors['hover']),
            ("!selected", colors['bg_darker'])
        ],
        foreground=[
            ("selected", colors['primary']),
            ("!selected", colors['text'])
        ]
    )

    # Configure Canvas background for server list
    root.option_add("*Canvas.background", colors['bg_darker'])
    root.option_add("*Canvas.highlightthickness", 0)

    # Configure modern scrollbar style - removed borders
    style.configure(
        "TScrollbar",
        background=colors['bg_darker'],
        troughcolor=colors['bg_darker'],
        borderwidth=0,
        relief="flat",
        arrowsize=0,
        width=8  # Made scrollbar thinner
    )

    style.map(
        "TScrollbar",
        background=[
            ("active", colors['active']),
            ("!active", colors['hover'])  # Made inactive state more visible
        ]
    )

    style.configure(
        "Canvas.TFrame",
        background=colors['bg_dark']
    )