from tkinter import ttk
import tkinter as tk

def apply_styles(root):
    """Apply custom dark mode styles to the application"""
    style = ttk.Style(root)

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

    # Force default theme for consistency
    style.theme_use('default')

    # Configure root window
    root.configure(bg=colors['bg_dark'])
    style.configure('.', background=colors['bg_dark'])

    # Configure global options for all widgets
    root.option_add('*Background', colors['bg_dark'])
    root.option_add('*background', colors['bg_dark'])
    root.option_add('*Foreground', colors['text'])
    root.option_add('*foreground', colors['text'])
    root.option_add('*selectBackground', colors['primary'])
    root.option_add('*selectForeground', colors['bg_dark'])

    # Configure all ttk widgets default background
    for widget in ['TFrame', 'TLabel', 'TButton', 'TEntry', 'TLabelframe', 'Treeview']:
        style.configure(widget, background=colors['bg_dark'])
        style.configure(widget, foreground=colors['text'])

    # Text widget configuration
    root.option_add("*Text.background", colors['bg_darker'])
    root.option_add("*Text.foreground", colors['text'])
    root.option_add("*Text.selectBackground", colors['primary'])
    root.option_add("*Text.selectForeground", colors['bg_dark'])
    root.option_add("*Text.highlightThickness", 0)
    root.option_add("*Text.highlightBackground", colors['bg_dark'])
    root.option_add("*Text.highlightColor", colors['primary'])

    # Configure Entry widget styles
    style.configure(
        "TEntry",
        fieldbackground=colors['bg_darker'],
        foreground=colors['text'],
        insertcolor=colors['text'],
        selectbackground=colors['primary'],
        selectforeground=colors['bg_dark']
    )

    # Configure frame styles
    style.configure(
        "TFrame",
        background=colors['bg_dark']
    )

    style.configure(
        "Card.TFrame",
        background=colors['bg_darker']
    )

    # Configure labelframe styles
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

    # Configure drop zone styles
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

    # Configure button styles
    style.configure(
        "Accent.TButton",
        background=colors['primary'],
        foreground=colors['bg_dark'],
        font=("Segoe UI", 10, "bold"),
        padding=(20, 10),
        relief="flat",
        borderwidth=0
    )

    style.map(
        "Accent.TButton",
        background=[
            ("active", colors['accent']),
            ("disabled", colors['bg_darker'])
        ],
        foreground=[
            ("active", colors['bg_dark']),
            ("disabled", colors['text_secondary'])
        ]
    )

    # Configure Treeview styles - Windows-specific fixes
    style.layout("ServerList.Treeview", [('ServerList.Treeview.treearea', {'sticky': 'nswe'})])

    # Configure Treeview colors for Windows
    style.configure(
        "ServerList.Treeview",
        background=colors['bg_darker'],
        foreground=colors['text'],
        fieldbackground=colors['bg_darker'],
        borderwidth=0,
        font=("Segoe UI", 12),
        rowheight=50,
        padding=(15, 8)
    )

    # Map Treeview colors for different states
    style.map(
        "ServerList.Treeview",
        background=[
            ("selected", colors['hover']),
            ("active", colors['active'])
        ],
        foreground=[
            ("selected", colors['text']),
            ("active", colors['text'])
        ],
        fieldbackground=[("!disabled", colors['bg_darker'])]  # Windows-specific fix
    )

    # Configure Treeview heading style
    style.configure(
        "ServerList.Treeview.Heading",
        background=colors['bg_darker'],
        foreground=colors['text'],
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 12, "bold")
    )

    style.map(
        "ServerList.Treeview.Heading",
        background=[("active", colors['hover'])]
    )

    # Configure Canvas background
    root.option_add("*Canvas.background", colors['bg_darker'])
    root.option_add("*Canvas.highlightthickness", 0)

    # Configure modern scrollbar style
    style.configure(
        "TScrollbar",
        background=colors['bg_darker'],
        troughcolor=colors['bg_darker'],
        borderwidth=0,
        relief="flat",
        arrowsize=0,
        width=8
    )

    style.map(
        "TScrollbar",
        background=[
            ("active", colors['active']),
            ("!active", colors['hover'])
        ]
    )

    # Configure Toplevel dialog styles with Windows-specific fixes
    root.option_add("*Toplevel.background", colors['bg_dark'])
    root.option_add("*Dialog.background", colors['bg_dark'])
    root.option_add("*Dialog.TFrame.background", colors['bg_dark'])
    root.option_add("*Dialog.TLabel.background", colors['bg_dark'])
    root.option_add("*Dialog.TButton.background", colors['bg_dark'])

    # Configure message boxes
    root.option_add("*Message.background", colors['bg_dark'])
    root.option_add("*Message.foreground", colors['text'])
    root.option_add("*Dialog.msg.background", colors['bg_dark'])
    root.option_add("*Dialog.msg.foreground", colors['text'])

    # Configure menus
    root.option_add("*Menu.background", colors['bg_darker'])
    root.option_add("*Menu.foreground", colors['text'])
    root.option_add("*Menu.selectColor", colors['primary'])
    root.option_add("*Menu.activeBackground", colors['hover'])
    root.option_add("*Menu.activeForeground", colors['text'])

    # Configure Text and ScrolledText widget styles
    root.option_add("*Text.background", colors['bg_darker'])
    root.option_add("*Text.foreground", colors['text'])
    root.option_add("*Text.selectBackground", colors['primary'])
    root.option_add("*Text.selectForeground", colors['bg_dark'])
    root.option_add("*Text.insertBackground", colors['text'])

    root.option_add("*ScrolledText.background", colors['bg_darker'])
    root.option_add("*ScrolledText.foreground", colors['text'])
    root.option_add("*ScrolledText.selectBackground", colors['primary'])
    root.option_add("*ScrolledText.selectForeground", colors['bg_dark'])
    root.option_add("*ScrolledText.insertBackground", colors['text'])