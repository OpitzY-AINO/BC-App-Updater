import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
from ui.drag_drop import DragDropZone
from ui.styles import apply_styles
from utils.json_parser import parse_server_config
from utils.powershell_manager import execute_powershell, publish_to_environment
from utils.config_manager import ConfigurationManager
from utils.translations import get_text
import os

class BusinessCentralPublisher(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title(get_text('app_title'))
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Application state
        self.app_file_path = None
        self.config_manager = ConfigurationManager()

        # Configure main window grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Apply styles first
        apply_styles(self)
        self.setup_ui()

        # Load saved configurations
        self.update_server_list()

    def setup_ui(self):
        """Set up the user interface with grid layout"""
        # Main container with increased padding
        main_frame = ttk.Frame(self, padding="30", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for main_frame
        main_frame.grid_rowconfigure(3, weight=3)  # Server list row
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        header = ttk.Label(
            main_frame,
            text=get_text('app_title'),
            style="Header.TLabel"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Extension File Section with reduced padding
        app_frame = ttk.LabelFrame(main_frame, text=get_text('extension_file'), padding="10", style="TLabelframe")
        app_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.app_drop_zone = DragDropZone(
            app_frame,
            get_text('drop_app'),
            self.handle_app_drop,
            ['.app']
        )
        self.app_drop_zone.pack(fill=tk.X, padx=5, pady=5)

        # Server Configuration Section with reduced padding
        config_frame = ttk.LabelFrame(main_frame, text=get_text('server_config'), padding="10", style="TLabelframe")
        config_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Inner frame for drop zone and text area
        config_inner = ttk.Frame(config_frame, style="TFrame")
        config_inner.pack(fill=tk.X, expand=True)

        # Left side: Drop zone
        drop_frame = ttk.Frame(config_inner, style="TFrame")
        drop_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.config_drop_zone = DragDropZone(
            drop_frame,
            get_text('drop_json'),
            self.handle_config_drop,
            ['.json']
        )
        self.config_drop_zone.pack(fill=tk.BOTH, expand=True)

        # Right side: buttons only
        button_frame = ttk.Frame(config_inner, style="TFrame")
        button_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Clear and Editor buttons
        clear_btn = ttk.Button(
            button_frame,
            text=get_text('clear'),
            command=self.clear_all,
            style="Accent.TButton"
        )
        clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        editor_btn = ttk.Button(
            button_frame,
            text=get_text('open_editor'),
            command=self.open_editor_popup,
            style="Accent.TButton"
        )
        editor_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)


        # Server List Section with increased size
        list_frame = ttk.LabelFrame(main_frame, text=get_text('server_configs'), padding="10", style="TLabelframe")
        list_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # Configure grid weights to give more space to the server list
        main_frame.grid_rowconfigure(3, weight=3)  # Increased weight for server list
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Server list with scrollbar
        list_container = ttk.Frame(list_frame, style="TFrame")
        list_container.grid(row=0, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        # Create Treeview first
        self.server_tree = ttk.Treeview(
            list_container,
            columns=("selected", "type", "name", "environment"),
            show="headings",
            style="ServerList.Treeview",
            height=10  # Set minimum number of visible items
        )

        # Configure columns with translated headers
        self.server_tree.heading("selected", text=get_text('col_select'), anchor="center")
        self.server_tree.heading("type", text=get_text('col_type'), anchor="center")
        self.server_tree.heading("name", text=get_text('col_name'), anchor="center")
        self.server_tree.heading("environment", text=get_text('col_environment'), anchor="center")

        # Configure column widths and alignment
        self.server_tree.column("selected", width=120, stretch=False, anchor="center")  # Further increased width
        self.server_tree.column("type", width=150, stretch=False, anchor="center")      # Increased width more
        self.server_tree.column("name", width=300, stretch=True, anchor="center")       # Increased width more
        self.server_tree.column("environment", width=400, stretch=True, anchor="center") # Increased width more

        self.server_tree.pack(fill=tk.BOTH, expand=True)

        tree_scrollbar = ttk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.server_tree.yview,
            style="TScrollbar"
        )

        self.server_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.server_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")

        self.server_tree.bind('<Button-1>', self.handle_server_click)

        # Publish Button Section
        button_container = ttk.Frame(main_frame, style="TFrame")
        button_container.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        self.publish_button = ttk.Button(
            button_container,
            text=get_text('publish_button'),
            command=self.publish_extension,
            style="Accent.TButton"
        )
        self.publish_button.pack(fill=tk.X)

    def publish_extension(self):
        """Handle the publish button click event"""
        if not self.app_file_path:
            messagebox.showerror("Error", get_text('select_app'))
            return

        selected_items = self.server_tree.get_children()
        selected_configs = []
        for item in selected_items:
            values = self.server_tree.item(item)['values']
            if values[0] == "☑":
                index = int(item.split('_')[1])
                if 0 <= index < len(self.config_manager.get_configurations()):
                    selected_configs.append(self.config_manager.get_configurations()[index])

        if not selected_configs:
            messagebox.showerror("Error", get_text('select_server'))
            return

        # Confirm deployment
        app_name = os.path.basename(self.app_file_path)
        selected_count = len(selected_configs)
        if not messagebox.askyesno(
            "Confirm Deployment",
            get_text('confirm_deployment', app_name=app_name, count=selected_count),
        ):
            return

        deployment_results = []

        try:
            # Create progress dialog
            progress_window = tk.Toplevel(self)
            progress_window.title(get_text('deployment_progress'))
            progress_window.geometry("400x300")
            progress_window.transient(self)
            progress_window.grab_set()

            # Configure progress window
            progress_frame = ttk.Frame(progress_window, padding="20", style="Card.TFrame")
            progress_frame.pack(fill=tk.BOTH, expand=True)

            # Add text widget for progress
            progress_text = scrolledtext.ScrolledText(
                progress_frame,
                height=10,
                font=("Consolas", 10),
                bg='#181825',
                fg='#cdd6f4',
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                padx=10,
                pady=10
            )
            progress_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Add close button (initially disabled)
            close_btn = ttk.Button(
                progress_frame,
                text=get_text('close'),
                command=progress_window.destroy,
                state="disabled",
                style="Accent.TButton"
            )
            close_btn.pack(fill=tk.X)

            # Update progress text
            def update_progress(message):
                progress_text.insert(tk.END, f"{message}\n")
                progress_text.see(tk.END)
                progress_text.update()

            # Deploy to each selected server
            for config in selected_configs:
                update_progress(get_text('deploying_to', server=config['name']))

                success, message = publish_to_environment(self.app_file_path, config)
                deployment_results.append((config['name'], success, message))

                # Update progress with result
                status = "✓" if success else "✗"
                update_progress(f"{status} {message}")

            # Show final summary
            update_progress(f"\n{get_text('deployment_summary')}")
            successful = sum(1 for _, success, _ in deployment_results if success)
            failed = len(deployment_results) - successful
            update_progress(get_text('successful', count=successful))
            update_progress(get_text('failed', count=failed))

            # Enable close button
            close_btn.configure(state="normal")

            # Show error message if any deployments failed
            if failed > 0:
                messagebox.showerror(
                    get_text('deployment_complete'),
                    get_text('deployment_complete_with_errors', count=failed)
                )
            else:
                messagebox.showinfo(
                    get_text('deployment_complete'),
                    get_text('all_deployments_successful')
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def handle_app_drop(self, file_path):
        """Handle dropping an app file"""
        if file_path.lower().endswith('.app'):
            self.app_file_path = file_path
            self.app_drop_zone.update_text(f"Selected: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Error", get_text('invalid_app'))

    def clear_all(self):
        """Clear server configurations"""
        # Clear configurations from manager
        self.config_manager.clear_configurations()
        # Update server list to reflect cleared state
        self.update_server_list()
        # Reset drop zone text
        self.config_drop_zone.update_text(get_text('drop_json'))

    def handle_server_click(self, event):
        """Handle clicks on server rows"""
        region = self.server_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.server_tree.identify_column(event.x)
            item = self.server_tree.identify_row(event.y)

            if column == "#1" and item:  # Checkbox column
                # Toggle selection state with larger symbols
                current_values = self.server_tree.item(item)['values']
                new_values = list(current_values)
                new_values[0] = "☑" if current_values[0] == "☐" else "☐"
                self.server_tree.item(item, values=new_values)

    def process_config(self, config_data):
        try:
            new_configs = parse_server_config(config_data)
            self.config_manager.add_configurations(new_configs)
            self.update_server_list()
            self.config_drop_zone.update_text(f"Loaded {len(new_configs)} server configurations")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process configuration: {str(e)}")

    def update_server_list(self):
        """Update the server list with current configurations"""
        # Clear existing items
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)

        # Add items from configuration manager
        for i, config in enumerate(self.config_manager.get_configurations()):
            env_type = config['environmentType']
            name = config['name']

            # Set the environment/instance detail based on type
            if env_type.lower() == 'sandbox':
                environment = config['environmentName']
            else:  # OnPrem
                environment = config['serverInstance']

            # Insert item with checkbox (using larger symbols for better visibility)
            self.server_tree.insert(
                "",
                tk.END,
                f"server_{i}",
                values=("☐", env_type, name, environment)
            )

    def handle_config_drop(self, file_path):
        """Handle dropping a configuration file"""
        try:
            with open(file_path, 'r') as f:
                config_text = f.read()

                # Preprocess the JSON text
                processed_text = preprocess_json_text(config_text)

                # Try to parse the configuration
                config_data = json.loads(processed_text)
                self.process_config(config_data)

        except json.JSONDecodeError as e:
            line_no = int(str(e).split('line')[1].split()[0])
            col_no = int(str(e).split('column')[1].split()[0])
            error_msg = get_text('json_format_error', error=str(e), line=line_no, col=col_no)
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", get_text('invalid_json'))

    def open_editor_popup(self):
        """Open a popup window with a larger text editor"""
        popup = tk.Toplevel(self)
        popup.title(get_text('config_editor'))
        popup.geometry("800x600")
        popup.minsize(600, 400)
        popup.transient(self)

        # Configure popup grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        # Create main frame with padding
        editor_frame = ttk.Frame(popup, style="Card.TFrame", padding="20")
        editor_frame.grid(row=0, column=0, sticky="nsew")
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        # Create text widget with syntax highlighting
        editor = tk.Text(
            editor_frame,
            font=("Consolas", 12),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            bg='#181825',
            fg='#cdd6f4',
            padx=10,
            pady=10
        )

        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            editor_frame,
            orient="vertical",
            command=editor.yview,
            style="TScrollbar"
        )

        editor.configure(yscrollcommand=scrollbar.set)

        # Layout
        editor.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Button frame
        button_frame = ttk.Frame(editor_frame, style="TFrame")
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(20, 0))

        # Load Current button
        load_btn = ttk.Button(
            button_frame,
            text=get_text('load_current'),
            style="Accent.TButton",
            command=lambda: self.load_current_configs(editor)
        )
        load_btn.pack(side=tk.LEFT)

        # Close button
        close_btn = ttk.Button(
            button_frame,
            text=get_text('close'),
            style="Accent.TButton",
            command=popup.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Apply button
        apply_btn = ttk.Button(
            button_frame,
            text=get_text('apply_changes'),
            style="Accent.TButton",
            command=lambda: self.apply_editor_changes(editor.get("1.0", tk.END), popup)
        )
        apply_btn.pack(side=tk.RIGHT)

        # Focus the editor
        editor.focus_set()

        # Make the popup modal
        popup.grab_set()

    def apply_editor_changes(self, new_text, popup):
        """Apply changes from popup editor to main window"""
        try:
            # Validate JSON before applying
            if new_text.strip():
                config_data = json.loads(new_text)
                self.process_config(config_data)

            # Close popup
            popup.destroy()

        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Error",
                get_text('json_format_error', error=str(e), line=e.lineno, col=e.colno)
            )

    def load_current_configs(self, editor):
        """Load current configurations into the editor"""
        current_configs = self.config_manager.get_configurations()
        if current_configs:
            # Convert to proper JSON format
            json_text = json.dumps(
                {"version": "0.4.0", "configurations": current_configs},
                indent=2
            )
            # Clear current content and insert new
            editor.delete("1.0", tk.END)
            editor.insert("1.0", json_text)
        else:
            messagebox.showinfo("Info", get_text('no_configs'))

def preprocess_json_text(json_text):
    """
    Preprocess JSON text to handle common formatting issues.

    Args:
        json_text (str): Raw JSON text

    Returns:
        str: Preprocessed JSON text
    """
    # Remove trailing commas before arrays and objects
    processed_text = json_text.replace(",]", "]").replace(",}", "}")
    processed_text = processed_text.replace(",\n]", "\n]").replace(",\n}", "\n}")

    try:
        # Try to parse as JSON first
        config = json.loads(processed_text)
        # If it's already a valid configuration object (has version and configurations)
        if isinstance(config, dict) and 'version' in config and 'configurations' in config:
            return processed_text
    except json.JSONDecodeError:
        pass

    # Check if we have multiple objects without array brackets
    stripped = processed_text.strip()
    if stripped.count('{') > 1 and not (stripped.startswith('[') and stripped.endswith(']')):
        # Wrap in array brackets if not already wrapped and contains multiple objects
        processed_text = f'[{processed_text}]'

    return processed_text

if __name__ == "__main__":
    app = BusinessCentralPublisher()
    app.mainloop()