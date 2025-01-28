import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import *
import os

class DragDropZone(ttk.Frame):
    def __init__(self, parent, text, callback, file_types=None):
        super().__init__(parent, style="Card.TFrame")
        self.callback = callback
        self.file_types = file_types or []

        # Create the drop zone with explicit background and style
        self.drop_target = ttk.Label(
            self,
            text=text,
            padding=20,
            style="DropZone.TLabel"
        )
        self.drop_target.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Bind events
        self.drop_target.bind('<Button-1>', self.browse_file)
        self.drop_target.bind('<Enter>', self.on_enter)
        self.drop_target.bind('<Leave>', self.on_leave)

        # Register drag-and-drop events
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_target.dnd_bind('<<DragEnter>>', self.handle_drag_enter)
        self.drop_target.dnd_bind('<<DragLeave>>', self.handle_drag_leave)

    def browse_file(self, event=None):
        """Handle click-to-browse functionality"""
        filetypes = [(f"{ext.upper()} files", f"*{ext}") for ext in self.file_types]
        filetypes.append(("All files", "*.*"))

        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.callback(filename)

    def handle_drop(self, event):
        """Handle file drop event"""
        file_path = event.data

        # Remove curly braces if present (Windows DnD quirk)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        if self.file_types:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.file_types:
                return

        self.callback(file_path)
        self.drop_target.configure(style="DropZone.TLabel")

    def handle_drag_enter(self, event):
        """Visual feedback when dragging over the zone"""
        self.drop_target.configure(style="DropZoneActive.TLabel")

    def handle_drag_leave(self, event):
        """Reset visual feedback when leaving the zone"""
        self.drop_target.configure(style="DropZone.TLabel")

    def on_enter(self, event):
        """Mouse hover effect"""
        self.drop_target.configure(style="DropZoneHover.TLabel")

    def on_leave(self, event):
        """Reset mouse hover effect"""
        self.drop_target.configure(style="DropZone.TLabel")

    def update_text(self, text):
        """Update the display text"""
        self.drop_target.configure(text=text)
