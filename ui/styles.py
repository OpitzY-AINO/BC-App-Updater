from tkinter import ttk
import tkinter as tk

def apply_styles(root):
    """Apply custom styles to the application"""
    style = ttk.Style()
    
    # Configure colors
    bg_color = "#ffffff"
    accent_color = "#007acc"
    hover_color = "#e8e8e8"
    active_color = "#cce4f7"
    
    # Configure main window
    root.configure(bg=bg_color)
    
    # Configure frame styles
    style.configure(
        "TFrame",
        background=bg_color
    )
    
    style.configure(
        "TLabelframe",
        background=bg_color
    )
    
    style.configure(
        "TLabelframe.Label",
        background=bg_color,
        font=("Segoe UI", 10)
    )
    
    # Configure drop zone styles
    style.configure(
        "DropZone.TLabel",
        background="#f0f0f0",
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=1
    )
    
    style.configure(
        "DropZoneHover.TLabel",
        background=hover_color,
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=1
    )
    
    style.configure(
        "DropZoneActive.TLabel",
        background=active_color,
        font=("Segoe UI", 11),
        padding=20,
        relief="solid",
        borderwidth=1
    )
    
    # Configure button styles
    style.configure(
        "TButton",
        background=accent_color,
        font=("Segoe UI", 10),
        padding=10
    )
    
    style.map(
        "TButton",
        background=[("active", accent_color)],
        relief=[("pressed", "sunken")]
    )
    
    # Configure checkbox styles
    style.configure(
        "TCheckbutton",
        background=bg_color,
        font=("Segoe UI", 10)
    )
    
    # Configure label styles
    style.configure(
        "TLabel",
        background=bg_color,
        font=("Segoe UI", 10)
    )
