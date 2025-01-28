import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
from ui.drag_drop import DragDropZone
from ui.styles import apply_styles
from utils.json_parser import parse_server_config
from utils.powershell_manager import execute_powershell
import os

class BusinessCentralPublisher(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Business Central Extension Publisher")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Application state
        self.app_file_path = None
        self.server_configs = []

        self.setup_ui()
        apply_styles(self)

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(
            main_frame,
            text="Business Central Extension Publisher",
            style="Header.TLabel"
        )
        header.pack(fill=tk.X, pady=(0, 20))

        # Top section for file uploads
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # App file drop zone in its own frame
        app_frame = ttk.LabelFrame(top_frame, text="Extension File", padding="10")
        app_frame.pack(fill=tk.X, pady=(0, 10))

        self.app_drop_zone = DragDropZone(
            app_frame,
            "Drop .app file here\nor click to browse",
            self.handle_app_drop,
            ['.app']
        )
        self.app_drop_zone.pack(fill=tk.X)

        # Server configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 20))

        # Config input methods container
        config_methods = ttk.Frame(config_frame)
        config_methods.pack(fill=tk.X)

        # Left side: Drop zone
        drop_frame = ttk.Frame(config_methods)
        drop_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.config_drop_zone = DragDropZone(
            drop_frame,
            "Drop server config JSON here\nor click to browse",
            self.handle_config_drop,
            ['.json']
        )
        self.config_drop_zone.pack(fill=tk.BOTH, expand=True)

        # Right side: Text input
        text_frame = ttk.Frame(config_methods)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.config_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            width=40,
            font=("Consolas", 10)
        )
        self.config_text.pack(fill=tk.BOTH, expand=True)

        # Parse button
        parse_btn = ttk.Button(
            text_frame,
            text="Parse Configuration",
            command=self.parse_text_config,
            style="Accent.TButton"
        )
        parse_btn.pack(fill=tk.X, pady=(5, 0))

        # Server list section
        list_frame = ttk.LabelFrame(main_frame, text="Server Configurations", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Server list with modern styling
        self.server_list = ttk.Frame(list_frame, style="ServerList.TFrame")
        self.server_list.pack(fill=tk.BOTH, expand=True)

        # Scrollable server list
        scrollbar = ttk.Scrollbar(self.server_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.servers_canvas = tk.Canvas(
            self.server_list,
            yscrollcommand=scrollbar.set,
            background='#ffffff',
            highlightthickness=0
        )
        self.servers_frame = ttk.Frame(self.servers_canvas)

        scrollbar.config(command=self.servers_canvas.yview)

        self.servers_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.servers_canvas.create_window((0, 0), window=self.servers_frame, anchor='nw')

        self.servers_frame.bind('<Configure>', lambda e: self.servers_canvas.configure(
            scrollregion=self.servers_canvas.bbox('all')
        ))

        # Publish button
        self.publish_button = ttk.Button(
            main_frame,
            text="Publish to Selected Servers",
            command=self.publish_extension,
            style="Accent.TButton"
        )
        self.publish_button.pack(fill=tk.X)

        # Bind paste event
        self.bind('<Control-v>', self.handle_paste)

    def parse_text_config(self):
        """Parse configuration from text input"""
        try:
            config_text = self.config_text.get("1.0", tk.END).strip()
            if not config_text:
                messagebox.showerror("Error", "Please enter configuration JSON")
                return

            config_data = json.loads(config_text)
            self.process_config(config_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse configuration: {str(e)}")

    def handle_app_drop(self, file_path):
        if file_path.lower().endswith('.app'):
            self.app_file_path = file_path
            self.app_drop_zone.update_text(f"Selected: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Error", "Please select a valid .app file")

    def handle_config_drop(self, file_path):
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            self.process_config(config_data)

            # Show the config in the text area
            self.config_text.delete("1.0", tk.END)
            self.config_text.insert("1.0", json.dumps(config_data, indent=2))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def handle_paste(self, event):
        """Handle paste event from clipboard"""
        try:
            # Try getting the clipboard content with fallbacks
            try:
                clipboard = self.clipboard_get()
            except tk.TclError:
                try:
                    clipboard = self.selection_get(selection='CLIPBOARD')
                except tk.TclError:
                    messagebox.showerror("Error", "Failed to get clipboard content")
                    return

            # Update text area with clipboard content
            self.config_text.delete("1.0", tk.END)
            self.config_text.insert("1.0", clipboard)

            try:
                # Try parsing the JSON
                config_data = json.loads(clipboard)
                self.process_config(config_data)
            except json.JSONDecodeError:
                # Don't show error immediately as user might be still editing
                pass
            except Exception as e:
                messagebox.showerror("Error", f"Invalid configuration format: {str(e)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process clipboard content: {str(e)}")

    def process_config(self, config_data):
        try:
            self.server_configs = parse_server_config(config_data)
            self.update_server_list()
            self.config_drop_zone.update_text(f"Loaded {len(self.server_configs)} server configurations")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process configuration: {str(e)}")

    def update_server_list(self):
        # Clear existing items
        for widget in self.servers_frame.winfo_children():
            widget.destroy()

        # Add new items with modern styling
        for config in self.server_configs:
            frame = ttk.Frame(self.servers_frame)
            frame.pack(fill=tk.X, pady=5, padx=5)

            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(frame, variable=var)
            cb.pack(side=tk.LEFT)

            name_label = ttk.Label(
                frame,
                text=f"{config['name']} ({config['environmentName']})"
            )
            name_label.pack(side=tk.LEFT, padx=5)

            config['checkbox_var'] = var

    def publish_extension(self):
        if not self.app_file_path:
            messagebox.showerror("Error", "Please select an app file first")
            return

        selected_configs = [
            config for config in self.server_configs
            if config['checkbox_var'].get()
        ]

        if not selected_configs:
            messagebox.showerror("Error", "Please select at least one server")
            return

        try:
            for config in selected_configs:
                # Example PowerShell command - to be replaced with actual implementation
                ps_command = f"""
                Write-Host "Publishing {os.path.basename(self.app_file_path)} to {config['name']}"
                """
                execute_powershell(ps_command)

            messagebox.showinfo("Success", "Publishing completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to publish: {str(e)}")

if __name__ == "__main__":
    app = BusinessCentralPublisher()
    app.mainloop()