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
        # Main container with padding
        main_frame = ttk.Frame(self, padding="20", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for main_frame
        main_frame.grid_rowconfigure(2, weight=1)  # Server list row gets more space
        main_frame.grid_columnconfigure(0, weight=1)  # Left half
        main_frame.grid_columnconfigure(1, weight=1)  # Right half

        # Header
        header = ttk.Label(
            main_frame,
            text=get_text('app_title'),
            style="Header.TLabel"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Left side container for both dropzones
        left_frame = ttk.Frame(main_frame, style="TFrame")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)  # Allow horizontal expansion

        # Extension File Section
        app_frame = ttk.LabelFrame(left_frame, text=get_text('extension_file'), padding="10", style="TLabelframe")
        app_frame.pack(fill=tk.X, pady=(0, 10))  # Increased bottom padding

        self.app_drop_zone = DragDropZone(
            app_frame,
            get_text('drop_app'),
            self.handle_app_drop,
            ['.app']
        )
        self.app_drop_zone.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Server Configuration Dropzone
        config_frame = ttk.LabelFrame(left_frame, text=get_text('server_config'), padding="10", style="TLabelframe")
        config_frame.pack(fill=tk.X)

        self.config_drop_zone = DragDropZone(
            config_frame,
            get_text('drop_json'),
            self.handle_config_drop,
            ['.json']
        )
        self.config_drop_zone.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Calculate total height of dropzones
        app_frame.update_idletasks()
        config_frame.update_idletasks()
        total_height = app_frame.winfo_reqheight() + config_frame.winfo_reqheight()

        # Right side: Text editor with matching height
        editor_frame = ttk.Frame(main_frame, style="TFrame")
        editor_frame.grid(row=1, column=1, sticky="nsew")
        editor_frame.grid_propagate(False)  # Prevent frame from resizing
        editor_frame.configure(height=total_height)  # Match height with left frame

        # Text area with scrollbar
        self.config_text = tk.Text(
            editor_frame,
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            bg='#181825',
            fg='#cdd6f4',
            padx=10,
            pady=10
        )

        text_scrollbar = ttk.Scrollbar(
            editor_frame,
            orient="vertical",
            command=self.config_text.yview,
            style="TScrollbar"
        )

        self.config_text.configure(yscrollcommand=text_scrollbar.set)
        self.config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button container centered below dropzones and editor
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        button_frame.columnconfigure(0, weight=1)  # Center the buttons

        # Clear and Parse buttons centered
        button_container = ttk.Frame(button_frame, style="TFrame")
        button_container.pack(expand=True)

        clear_btn = ttk.Button(
            button_container,
            text=get_text('clear'),
            command=self.clear_all,
            style="Accent.TButton",
            width=20  # Fixed width for consistency
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        parse_btn = ttk.Button(
            button_container,
            text=get_text('parse_config'),
            command=self.parse_text_config,
            style="Accent.TButton",
            width=20  # Fixed width for consistency
        )
        parse_btn.pack(side=tk.LEFT, padx=5)

        # Server List Section
        list_frame = ttk.LabelFrame(main_frame, text=get_text('server_configs'), padding="10", style="TLabelframe")
        list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        list_container = ttk.Frame(list_frame, style="TFrame")
        list_container.pack(fill=tk.BOTH, expand=True)

        # Set minimum height for the Treeview
        self.server_tree = ttk.Treeview(
            list_container,
            columns=("selected", "type", "name", "environment"),
            show="headings",
            style="ServerList.Treeview",
            height=10  # Set minimum number of visible items
        )

        # Configure columns with translated headers
        self.server_tree.heading("selected", text=get_text('col_select'))
        self.server_tree.heading("type", text=get_text('col_type'))
        self.server_tree.heading("name", text=get_text('col_name'))
        self.server_tree.heading("environment", text=get_text('col_environment'))

        self.server_tree.column("selected", width=60, stretch=False)
        self.server_tree.column("type", width=100, stretch=False)
        self.server_tree.column("name", width=200, stretch=True)
        self.server_tree.column("environment", width=300, stretch=True)

        tree_scrollbar = ttk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.server_tree.yview,
            style="TScrollbar"
        )

        self.server_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.server_tree.bind('<Button-1>', self.handle_server_click)

        # Publish Button Section
        publish_frame = ttk.Frame(main_frame, style="TFrame")
        publish_frame.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.publish_button = ttk.Button(
            publish_frame,
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
        """Clear both the text area and server configurations"""
        self.config_text.delete("1.0", tk.END)
        self.config_manager.clear_configurations()
        self.update_server_list()
        self.config_drop_zone.update_text(get_text('drop_json'))

    def handle_server_click(self, event):
        """Handle clicks on server rows"""
        region = self.server_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.server_tree.identify_column(event.x)
            item = self.server_tree.identify_row(event.y)

            if column == "#1" and item:  # Checkbox column
                # Toggle selection state
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

            # Insert item with checkbox
            self.server_tree.insert(
                "",
                tk.END,
                f"server_{i}",
                values=("☐", env_type, name, environment)
            )

    def parse_text_config(self):
        """Parse configuration from text input"""
        try:
            config_text = self.config_text.get("1.0", tk.END).strip()
            if not config_text:
                messagebox.showerror("Error", get_text('enter_config'))
                return

            # Preprocess the JSON text
            processed_text = preprocess_json_text(config_text)

            # Try to parse and format JSON
            config_data = json.loads(processed_text)

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

    def handle_config_drop(self, file_path):
        """Handle dropping a configuration file"""
        try:
            with open(file_path, 'r') as f:
                config_text = f.read()

                # Preprocess the JSON text
                processed_text = preprocess_json_text(config_text)

                # Try to parse the configuration
                config_data = json.loads(processed_text)

                # Format and display the properly formatted JSON
                formatted_json = json.dumps(config_data, indent=2)
                self.config_text.delete("1.0", tk.END)
                self.config_text.insert("1.0", formatted_json)

                self.process_config(config_data)

        except json.JSONDecodeError as e:
            line_no = int(str(e).split('line')[1].split()[0])
            col_no = int(str(e).split('column')[1].split()[0])
            error_msg = get_text('json_format_error', error=str(e), line=line_no, col=col_no)
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", get_text('invalid_json'))


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