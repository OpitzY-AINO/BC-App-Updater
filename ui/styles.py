from tkinter import ttk
import tkinter as tk

def apply_styles(root):
    """Apply custom styles to the application"""
    style = ttk.Style()

    # Modern color palette
    colors = {
        'bg': '#ffffff',
        'primary': '#2563eb',  # Modern blue
        'secondary': '#64748b', # Slate
        'hover': '#dbeafe',    # Light blue
        'active': '#bfdbfe',   # Slightly darker blue
        'border': '#e2e8f0',   # Subtle border
        'text': '#1e293b',     # Dark slate
        'text_secondary': '#64748b'  # Medium slate
    }

    # Configure main window
    root.configure(bg=colors['bg'])

    # Configure frame styles
    style.configure(
        "TFrame",
        background=colors['bg']
    )

    style.configure(
        "Card.TFrame",
        background=colors['bg'],
        borderwidth=1,
        relief="solid"
    )

    # Configure modern labelframe
    style.configure(
        "TLabelframe",
        background=colors['bg'],
        borderwidth=1,
        relief="solid"
    )

    style.configure(
        "TLabelframe.Label",
        background=colors['bg'],
        foreground=colors['text'],
        font=("Segoe UI", 11, "bold"),
        padding=(10, 5)
    )

    # Configure drop zone styles with modern look
    style.configure(
        "DropZone.TLabel",
        background=colors['bg'],
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

    # Configure modern button style
    style.configure(
        "Accent.TButton",
        background=colors['primary'],
        foreground='white',
        font=("Segoe UI", 10, "bold"),
        padding=(20, 10),
        borderwidth=0
    )

    style.map(
        "Accent.TButton",
        background=[("active", colors['hover'])],
        foreground=[("active", colors['primary'])]
    )

    # Configure checkbox styles
    style.configure(
        "TCheckbutton",
        background=colors['bg'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.map(
        "TCheckbutton",
        background=[("active", colors['bg'])],
        foreground=[("active", colors['primary'])]
    )

    # Configure label styles
    style.configure(
        "TLabel",
        background=colors['bg'],
        foreground=colors['text'],
        font=("Segoe UI", 10)
    )

    style.configure(
        "Header.TLabel",
        background=colors['bg'],
        foreground=colors['text'],
        font=("Segoe UI", 16, "bold"),
        padding=(0, 10)
    )

    # Configure canvas for server list
    style.configure(
        "ServerList.TFrame",
        background=colors['bg'],
        relief="solid",
        borderwidth=1
    )