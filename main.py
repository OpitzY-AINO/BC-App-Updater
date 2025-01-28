import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
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

        # Apply styles first
        apply_styles(self)
        self.setup_ui()

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header with modern styling
        header = ttk.Label(
            main_frame,
            text="Business Central Extension Publisher",
            style="Header.TLabel"
        )
        header.pack(fill=tk.X, pady=(0, 20))

        # Top section for file uploads
        top_frame = ttk.Frame(main_frame, style="TFrame")
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # App file drop zone in its own frame
        app_frame = ttk.LabelFrame(top_frame, text="Extension File", padding="10", style="TLabelframe")
        app_frame.pack(fill=tk.X, pady=(0, 10))

        self.app_drop_zone = DragDropZone(
            app_frame,
            "Drop .app file here\nor click to browse",
            self.handle_app_drop,
            ['.app']
        )
        self.app_drop_zone.pack(fill=tk.X, padx=5, pady=5)

        # Server configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="10", style="TLabelframe")
        config_frame.pack(fill=tk.X, pady=(0, 20))

        # Config input methods container
        config_methods = ttk.Frame(config_frame, style="TFrame")
        config_methods.pack(fill=tk.X)

        # Left side: Drop zone
        drop_frame = ttk.Frame(config_methods, style="TFrame")
        drop_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.config_drop_zone = DragDropZone(
            drop_frame,
            "Drop server config JSON here\nor click to browse",
            self.handle_config_drop,
            ['.json']
        )
        self.config_drop_zone.pack(fill=tk.BOTH, expand=True)

        # Right side: Text input
        text_frame = ttk.Frame(config_methods, style="TFrame")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Button container
        button_frame = ttk.Frame(text_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 5))

        # Clear and Parse buttons side by side
        clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all,
            style="Accent.TButton"
        )
        clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        parse_btn = ttk.Button(
            button_frame,
            text="Parse Configuration",
            command=self.parse_text_config,
            style="Accent.TButton"
        )
        parse_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        # Configuration text area with modern scrollbar
        self.config_text = tk.Text(
            text_frame,
            height=8,
            width=40,
            font=("Consolas", 10),
            relief="solid",
            borderwidth=1,
            bg='#181825',
            fg='#cdd6f4',
        )

        # Create and configure modern scrollbar for text
        text_scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.config_text.yview,
            style="TScrollbar"
        )

        self.config_text.configure(yscrollcommand=text_scrollbar.set)

        # Pack text and scrollbar
        self.config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Server list section with Treeview
        list_frame = ttk.LabelFrame(main_frame, text="Server Configurations", padding="10", style="TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Create Treeview for server list
        self.server_tree = ttk.Treeview(
            list_frame,
            columns=("type", "name", "environment"),
            show="headings",
            selectmode="browse",  # Changed to allow selection
            style="ServerList.Treeview"
        )

        # Configure columns
        self.server_tree.heading("type", text="Type")
        self.server_tree.heading("name", text="Name")
        self.server_tree.heading("environment", text="Environment")

        # Set column widths
        self.server_tree.column("type", width=100, stretch=False)
        self.server_tree.column("name", width=200, stretch=True)
        self.server_tree.column("environment", width=300, stretch=True)

        # Create scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.server_tree.yview,
            style="TScrollbar"
        )

        self.server_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Pack Treeview and scrollbar
        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)


        # Bind click handler
        self.server_tree.bind('<Button-1>', self.handle_server_click)


        # Publish button with accent styling
        self.publish_button = ttk.Button(
            main_frame,
            text="Publish to Selected Servers",
            command=self.publish_extension,
            style="Accent.TButton"
        )
        self.publish_button.pack(fill=tk.X)

    def handle_server_click(self, event):
        """Handle clicks on server rows"""
        region = self.server_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.server_tree.identify_row(event.y)
            if item:
                # Toggle selection state
                current_selection = self.server_tree.selection()
                if item in current_selection:
                    self.server_tree.selection_remove(item)
                else:
                    self.server_tree.selection_add(item)

    def process_config(self, config_data):
        try:
            self.server_configs = parse_server_config(config_data)
            self.update_server_list()
            self.config_drop_zone.update_text(f"Loaded {len(self.server_configs)} server configurations")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process configuration: {str(e)}")

    def update_server_list(self):
        # Clear existing items
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)

        # Add new items
        for i, config in enumerate(self.server_configs):
            env_type = config['environmentType']
            name = config['name']

            # Set the environment/instance detail based on type
            if env_type.lower() == 'sandbox':
                environment = config['environmentName']
            else:  # OnPrem
                environment = config['serverInstance']

            # Insert item with the new column structure
            self.server_tree.insert(
                "",
                tk.END,
                f"server_{i}",
                values=(env_type, name, environment)
            )

    def clear_all(self):
        """Clear both the text area and server configurations"""
        self.config_text.delete("1.0", tk.END)
        self.server_configs = []
        self.update_server_list()
        self.config_drop_zone.update_text("Drop server config JSON here\nor click to browse")

    def handle_app_drop(self, file_path):
        if file_path.lower().endswith('.app'):
            self.app_file_path = file_path
            self.app_drop_zone.update_text(f"Selected: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Error", "Please select a valid .app file")

    def handle_config_drop(self, file_path):
        try:
            with open(file_path, 'r') as f:
                config_text = f.read()

                # Remove trailing commas before arrays and objects
                config_text = config_text.replace(",]", "]")
                config_text = config_text.replace(",}", "}")
                config_text = config_text.replace(",\n]", "\n]")
                config_text = config_text.replace(",\n}", "\n}")

                # Try to parse the configuration
                config_data = json.loads(config_text)

                # Format and display the properly formatted JSON
                formatted_json = json.dumps(config_data, indent=2)
                self.config_text.delete("1.0", tk.END)
                self.config_text.insert("1.0", formatted_json)

                self.process_config(config_data)

        except json.JSONDecodeError as e:
            line_no = int(str(e).split('line')[1].split()[0])
            col_no = int(str(e).split('column')[1].split()[0])
            error_msg = f"JSON Format Error:\n{str(e)}\n\nPlease check line {line_no}, column {col_no} of your JSON configuration."
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def parse_text_config(self):
        """Parse configuration from text input"""
        try:
            config_text = self.config_text.get("1.0", tk.END).strip()
            if not config_text:
                messagebox.showerror("Error", "Please enter configuration JSON")
                return

            # Try to parse and format JSON
            config_data = json.loads(config_text)

            # Format and display the properly formatted JSON
            formatted_json = json.dumps(config_data, indent=2)
            self.config_text.delete("1.0", tk.END)
            self.config_text.insert("1.0", formatted_json)

            self.process_config(config_data)
        except json.JSONDecodeError as e:
            line_no = int(str(e).split('line')[1].split()[0])
            col_no = int(str(e).split('column')[1].split()[0])
            error_msg = f"JSON Format Error:\n{str(e)}\n\nPlease check line {line_no}, column {col_no} of your JSON configuration."
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse configuration: {str(e)}")

    def publish_extension(self):
        if not self.app_file_path:
            messagebox.showerror("Error", "Please select an app file first")
            return

        # Get selected items from Treeview
        selected_items = self.server_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select at least one server")
            return

        # Map selected items back to configurations
        selected_configs = []
        for item in selected_items:
            index = int(item.split('_')[1])
            if 0 <= index < len(self.server_configs):
                selected_configs.append(self.server_configs[index])

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

    def show_text_menu(self, event):
        """Show the right-click menu for the text area"""
        try:
            self.text_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_menu.grab_release()

    def paste_text(self):
        """Paste text from clipboard into the text area"""
        try:
            # Try to get clipboard content
            clipboard_text = self.clipboard_get()
            self.config_text.insert(tk.INSERT, clipboard_text)

            # Try to parse as JSON, but don't show error if it fails
            try:
                if clipboard_text.strip():
                    config_data = json.loads(clipboard_text)
                    self.process_config(config_data)
            except json.JSONDecodeError:
                # Ignore JSON parsing errors during paste
                pass

        except tk.TclError:
            # Ignore clipboard errors
            pass



if __name__ == "__main__":
    app = BusinessCentralPublisher()
    app.mainloop()