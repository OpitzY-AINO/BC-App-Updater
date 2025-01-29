import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os
from ui.drag_drop import DragDropZone
from ui.styles import apply_styles
from utils.json_parser import parse_server_config
from utils.powershell_manager import publish_to_environment, test_server_connection
from utils.config_manager import ConfigurationManager
from utils.translations import get_text
import uuid
import threading
from queue import Queue, Empty  # Import Empty explicitly
import logging
import traceback
from datetime import datetime, timedelta
from typing import List, Dict
#Added import for credential manager
from utils.credential_manager import CredentialManager


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PublishWorker(threading.Thread):
    def __init__(self, app_file_path: str, configs: List[Dict], credential_manager: CredentialManager, result_queue: Queue):
        super().__init__()
        self.app_file_path = app_file_path
        self.configs = configs
        self.credential_manager = credential_manager
        self.result_queue = result_queue
        self.daemon = True
        logger.debug("PublishWorker initialized")

    def run(self):
        try:
            logger.debug("Starting PublishWorker thread")
            for config in self.configs:
                if config['environmentType'].lower() == 'onprem':
                    server_id = f"{config['server']}_{config['serverInstance']}"
                    logger.debug(f"Processing server: {server_id}")

                    try:
                        # Get credentials from credential manager
                        creds = self.credential_manager.get_credentials(server_id)
                        if creds is None:
                            logger.error(f"No credentials found for {server_id}")
                            self.result_queue.put(('failed', config['name'], "Credentials not available"))
                            continue

                        logger.debug(f"Publishing to {server_id}")
                        success, message = publish_to_environment(
                            self.app_file_path,
                            config,
                            creds['username'],
                            creds['password']
                        )

                        self.result_queue.put(('progress', config['name'], success, message))

                    except Exception as e:
                        logger.error(f"Error publishing to {server_id}: {str(e)}\n{traceback.format_exc()}")
                        self.result_queue.put(('failed', config['name'], f"Error: {str(e)}"))

        except Exception as e:
            logger.error(f"Worker thread error: {str(e)}\n{traceback.format_exc()}")
            self.result_queue.put(('error', str(e)))

class BusinessCentralPublisher(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Force ttk to use custom style
        style = ttk.Style(self)
        style.theme_use('default')

        # Apply styles before any widget creation
        apply_styles(self)

        # Configure root window background
        self.configure(background='#1e1e2e')  # Dark background color

        # Set background for all tkinter widgets
        self.option_add('*Background', '#1e1e2e')
        self.option_add('*background', '#1e1e2e')
        self.option_add('*Foreground', '#cdd6f4')
        self.option_add('*foreground', '#cdd6f4')

        self.title(get_text('app_title'))
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Application state
        self.app_file_path = None
        self.config_manager = ConfigurationManager()
        #Added credential manager instance
        self.credential_manager = CredentialManager()

        # Configure main window grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup_ui()
        self.center_window(self)

        # Load saved configurations
        self.update_server_list()

    def center_window(self, window, width=None, height=None):
        """Center any window on the screen"""
        # If dimensions are provided, set them first
        if width is not None and height is not None:
            window.geometry(f"{width}x{height}")

        # Force window to update its geometry
        window.update_idletasks()

        # Get window size (either provided or current)
        if width is None:
            width = window.winfo_width()
        if height is None:
            height = window.winfo_height()

        # Calculate center position
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2

        # Set position
        window.geometry(f"{width}x{height}+{x}+{y}")

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

        # Extension File Section
        app_frame = ttk.LabelFrame(main_frame, text=get_text('extension_file'), padding="10", style="TLabelframe")
        app_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.app_drop_zone = DragDropZone(
            app_frame,
            get_text('drop_app'),
            self.handle_app_drop,
            ['.app']
        )
        self.app_drop_zone.pack(fill=tk.BOTH, expand=True)

        # Server Configuration Section
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

        # Right side: buttons
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

        # Server List Section
        list_frame = ttk.LabelFrame(main_frame, text=get_text('server_configs'), padding="10", style="TLabelframe")
        list_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Server list with scrollbar
        list_container = ttk.Frame(list_frame, style="TFrame")
        list_container.grid(row=0, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        # Create Treeview
        self.server_tree = ttk.Treeview(
            list_container,
            columns=("selected", "type", "name", "environment"),
            show="headings",
            style="ServerList.Treeview",
            height=10
        )

        # Configure tag for checked rows
        self.server_tree.tag_configure("checked", background='#313244')  # Use hover color for checked rows

        # Configure columns
        self.server_tree.heading("selected", text=get_text('col_select'), anchor="center")
        self.server_tree.heading("type", text=get_text('col_type'), anchor="center")
        self.server_tree.heading("name", text=get_text('col_name'), anchor="center")
        self.server_tree.heading("environment", text=get_text('col_environment'), anchor="center")

        # Configure column widths
        self.server_tree.column("selected", width=120, stretch=False, anchor="center")
        self.server_tree.column("type", width=150, stretch=False, anchor="center")
        self.server_tree.column("name", width=300, stretch=True, anchor="center")
        self.server_tree.column("environment", width=400, stretch=True, anchor="center")

        # Create scrollbar
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

        # Add Test Connection button next to the server list
        button_container = ttk.Frame(list_frame, style="TFrame")
        button_container.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        self.test_connection_btn = ttk.Button(
            button_container,
            text=get_text('test_connection'),
            command=self.test_selected_connections,
            state="disabled",
            style="Accent.TButton"
        )
        self.test_connection_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Publish Button Section
        button_container = ttk.Frame(main_frame, style="TFrame")
        button_container.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        self.publish_button = ttk.Button(
            button_container,
            text=get_text('publish_button'),
            command=self.publish_extension,
            state="disabled",
            style="Accent.TButton"
        )
        self.publish_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))

    def show_progress_window(self, title):
        """Create and center a progress window"""
        window = tk.Toplevel(self)
        window.title(title)
        window.transient(self)
        window.grab_set()  # Make modal

        # Configure window background
        window.configure(background='#1e1e2e')

        # Main frame with padding
        progress_frame = ttk.Frame(window, padding="20", style="Card.TFrame")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        progress_frame.configure(style="Dark.TFrame")

        # Add text widget for progress
        progress_text = scrolledtext.ScrolledText(
            progress_frame,
            height=20,
            font=("Consolas", 11),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        progress_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Add close button
        close_btn = ttk.Button(
            progress_frame,
            text=get_text('close'),
            command=window.destroy,
            style="Accent.TButton"
        )
        close_btn.pack(fill=tk.X)

        # Set size and center
        width = 800
        height = 600
        window.minsize(width, height)
        self.center_window(window, width, height)

        return window, progress_text, close_btn

    def publish_extension(self):
        """Handle publishing extension to selected servers"""
        if not self.app_file_path:
            messagebox.showerror("Error", get_text('select_app'))
            return

        selected_configs = []
        for item in self.server_tree.get_children():
            values = self.server_tree.item(item)['values']
            if values[0] == "☑":
                index = int(item.split('_')[1])
                if 0 <= index < len(self.config_manager.get_configurations()):
                    selected_configs.append(self.config_manager.get_configurations()[index])

        if not selected_configs:
            messagebox.showerror("Error", get_text('select_server'))
            return

        logger.debug("Starting publish process")
        logger.debug(f"Selected configs: {len(selected_configs)}")

        # Show progress window
        progress_window, progress_text, close_btn = self.show_progress_window(
            get_text('deployment_progress')
        )

        def update_progress(message):
            logger.debug(f"Progress update: {message}")
            progress_text.insert(tk.END, f"{message}\n")
            progress_text.see(tk.END)
            progress_text.update()

        update_progress("Starting deployment process...")

        # First collect all needed credentials
        credentials_collected = True
        for config in selected_configs:
            if config['environmentType'].lower() == 'onprem':
                server_id = f"{config['server']}_{config['serverInstance']}"
                update_progress(f"Checking credentials for {config['name']}...")
                logger.debug(f"Checking credentials for server: {server_id}")

                # Try to get existing credentials
                existing_creds = self.credential_manager.get_credentials(server_id)
                if not existing_creds:
                    update_progress(f"Requesting credentials for {config['name']}...")
                    logger.debug(f"Opening credential dialog for {server_id}")

                    # Bring progress window to front
                    progress_window.lift()
                    progress_window.focus_force()
                    progress_window.grab_set()
                    progress_window.update()

                    # Show credential dialog
                    username, password = self.show_credential_dialog(config)

                    if username and password:
                        logger.debug(f"Storing credentials for {server_id}")
                        self.credential_manager.store_credentials(server_id, username, password)
                        update_progress(f"✓ Credentials stored for {config['name']}")
                    else:
                        logger.debug(f"No credentials provided for {server_id}")
                        update_progress(f"✗ {config['name']}: No credentials provided")
                        credentials_collected = False
                        close_btn.configure(state="normal")
                        return
                else:
                    logger.debug(f"Using existing credentials for {server_id}")
                    update_progress(f"✓ Using stored credentials for {config['name']}")

        if not credentials_collected:
            return

        update_progress("\nStarting deployment to selected servers...")

        # Initialize tracking variables
        self.deployment_results = []
        self.result_queue = Queue()

        # Create and start worker thread
        logger.debug("Creating worker thread")
        worker = PublishWorker(
            self.app_file_path,
            selected_configs,
            self.credential_manager,
            self.result_queue
        )
        worker.start()
        logger.debug("Worker thread started")

        def show_summary():
            update_progress(f"\n{get_text('deployment_summary')}")
            successful = sum(1 for _, success, _ in self.deployment_results if success)
            failed = len(self.deployment_results) - successful
            update_progress(get_text('successful', count=successful))
            update_progress(get_text('failed', count=failed))
            close_btn.configure(state="normal")
            logger.debug("Summary displayed")

        self.show_summary = show_summary
        self.timeout = datetime.now() + timedelta(minutes=5)
        self.after(100, self.check_queue)

    def check_queue(self):
        """Check the result queue for updates and handle them"""
        try:
            # Check for timeout
            if datetime.now() >= self.timeout:
                logger.info("Publish operation timeout reached")
                # Handle timeout for remaining deployments
                remaining = len(self.selected_configs) - len(self.deployment_results)
                if remaining > 0:
                    self.update_progress("\nTimeout reached, marking remaining deployments as failed...")
                    for config in self.selected_configs:
                        if not any(result[0] == config['name'] for result in self.deployment_results):
                            self.deployment_results.append((config['name'], False, "Operation timed out"))
                            self.update_progress(f"✗ {config['name']}: Operation timed out")
                self.show_summary()
                return

            try:
                result = self.result_queue.get_nowait()
                logger.debug(f"Queue result received: {result[0]}")

                if result[0] == 'progress':
                    server_name, success, message = result[1], result[2], result[3]
                    self.deployment_results.append((server_name, success, message))
                    status = "✓" if success else "✗"
                    self.update_progress(f"{status} {server_name}: {message}")

                    if len(self.deployment_results) == len(self.selected_configs):
                        self.show_summary()
                        return

                elif result[0] == 'failed':
                    server_name, message = result[1], result[2]
                    logger.warning(f"Operation failed for {server_name}: {message}")
                    self.deployment_results.append((server_name, False, message))
                    self.update_progress(f"✗ {server_name}: {message}")

                    # Check if all servers are processed
                    if len(self.deployment_results) == len(self.selected_configs):
                        self.show_summary()
                        return

                elif result[0] == 'error':
                    logger.error(f"Error in publish operation: {result[1]}")
                    self.update_progress(f"Error: {result[1]}")
                    self.show_summary()
                    return

            except Empty:
                # No results available, schedule next check
                pass

            # Schedule next check with shorter interval
            self.after(50, self.check_queue)

        except Exception as e:
            logger.error(f"Error in check_queue: {str(e)}\n{traceback.format_exc()}")
            self.update_progress(f"Error checking progress: {str(e)}")

    def show_credential_dialog(self, server_config):
        """Show dialog to input server credentials"""
        dialog = tk.Toplevel(self)
        dialog.title("Server Authentication")
        dialog.transient(self)
        dialog.grab_set()

        # Configure dialog background and size
        dialog.configure(background='#1e1e2e')
        width = 400
        height = 300
        dialog.minsize(width, height)
        dialog.resizable(False, False)

        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding=20, style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(style="Dark.TFrame")

        # Header
        header_text = f"Authentication Required\n{server_config['name']}"
        header = ttk.Label(
            main_frame,
            text=header_text,
            style="Header.TLabel",
            justify=tk.CENTER,
            font=("Segoe UI", 14, "bold"),
            background='#1e1e2e',
            foreground='#cdd6f4'
        )
        header.pack(pady=(0, 20))

        # Username
        username_label = ttk.Label(
            main_frame,
            text="Username",
            background='#1e1e2e',
            foreground='#cdd6f4'
        )
        username_label.pack(anchor="w", pady=(0, 5))
        username_entry = ttk.Entry(main_frame)
        username_entry.pack(fill=tk.X, pady=(0, 15))

        # Password
        password_label = ttk.Label(
            main_frame,
            text="Password",
            background='#1e1e2e',
            foreground='#cdd6f4'
        )
        password_label.pack(anchor="w", pady=(0, 5))
        password_entry = ttk.Entry(main_frame, show="•")
        password_entry.pack(fill=tk.X, pady=(0, 20))

        result = {'username': None, 'password': None}

        def on_ok():
            result['username'] = username_entry.get()
            result['password'] = password_entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        button_frame.configure(style="Dark.TFrame")

        # Create equal-width buttons with consistent styling
        button_width = 15
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            style="Accent.TButton",
            width=button_width
        )
        connect_btn = ttk.Button(
            button_frame,
            text="Connect",
            command=on_ok,
            style="Accent.TButton",
            width=button_width
        )

        # Pack buttons with equal spacing
        cancel_btn.pack(side=tk.LEFT, padx=(0, 5), expand=True)
        connect_btn.pack(side=tk.RIGHT, padx=(5, 0), expand=True)

        # Center the dialog
        self.center_window(dialog, width, height)

        # Make dialog modal
        dialog.wait_window()

        return result['username'], result['password']

    def handle_app_drop(self, file_path):
        """Handle dropping an app file"""
        if file_path.lower().endswith('.app'):
            self.app_file_path = file_path
            self.app_drop_zone.update_text(f"Selected: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Error", get_text('invalid_app'))

    def clear_all(self):
        """Clear server configurations and associated credentials"""
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

                # Update both values and tags
                tags = ("checked",) if new_values[0] == "☑" else ()
                self.server_tree.item(item, values=new_values, tags=tags)

                # Update publish button state
                self.update_publish_button_state()

    def update_publish_button_state(self):
        """Update publish button and test connection button states based on selections"""
        has_selection = False
        for item in self.server_tree.get_children():
            if self.server_tree.item(item)['values'][0] == "☑":
                has_selection = True
                break

        new_state = "normal" if has_selection else "disabled"
        self.publish_button.configure(state=new_state)
        self.test_connection_btn.configure(state=new_state)

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
            item_id = f"server_{i}"
            self.server_tree.insert(
                "",
                tk.END,
                item_id,
                values=("☐", env_type, name, environment)
            )

        # Update publish button state after loading list
        self.update_publish_button_state()

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
        popup.transient(self)
        popup.grab_set()

        # Set size
        width = 800
        height = 600
        popup.minsize(width, height)
        popup.resizable(True, True)

        # Create main frame with padding
        editor_frame = ttk.Frame(popup, padding="20", style="Card.TFrame")
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Add text widget for config
        editor = scrolledtext.ScrolledText(
            editor_frame,
            height=20,
            font=("Consolas", 12),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        editor.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Button frame
        button_frame = ttk.Frame(editor_frame, style="TFrame")
        button_frame.pack(fill=tk.X)

        # Load Current button
        load_btn = ttk.Button(
            button_frame,
            text=get_text('load_current'),
            command=lambda: self.load_current_configs(editor),
            style="Accent.TButton"
        )
        load_btn.pack(side=tk.LEFT)

        # Apply button
        apply_btn = ttk.Button(
            button_frame,
            text=get_text('apply_changes'),
            command=lambda: self.apply_editor_changes(editor.get("1.0", tk.END), popup),
            style="Accent.TButton"
        )
        apply_btn.pack(side=tk.RIGHT, padx=5)

        # Close button
        close_btn = ttk.Button(
            button_frame,
            text=get_text('close'),
            command=popup.destroy,
            style="Accent.TButton"
        )
        close_btn.pack(side=tk.RIGHT)

        # Center the window
        self.center_window(popup, width, height)

        # Give focus to editor
        editor.focus_set()

    def apply_editor_changes(self, new_text, popup):
        """Apply changes from popup editor to main window"""
        try:
            # Validate JSON before applying
            if not new_text.strip():
                popup.destroy()
                return

            config_data = json.loads(new_text)

            # When editing existing configurations, replace them entirely
            if isinstance(config_data, dict) and 'configurations' in config_data:
                self.config_manager.replace_configurations(config_data['configurations'])
            else:
                # For new configurations (pasted/imported), use normal add process
                self.process_config(config_data)

            # Update the server list to reflect changes
            self.update_server_list()

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

    def test_selected_connections(self):
        """Test connection to selected servers"""
        selected_items = self.server_tree.get_children()
        selected_configs = []
        for item in selected_items:
            values = self.server_tree.item(item)['values']
            if values[0] == "☑":
                index = int(item.split('_')[1])
                if 0 <= index < len(self.config_manager.get_configurations()):
                    selected_configs.append(self.config_manager.get_configurations()[index])

        if not selected_configs:
            messagebox.showerror("Error", get_text('select_server_test'))
            return

        # Create and show progress window
        progress_window, progress_text, close_btn = self.show_progress_window(get_text('connection_test_progress'))

        def update_progress(message):
            progress_text.insert(tk.END, f"{message}\n")
            progress_text.see(tk.END)
            progress_text.update()

        # Test connection to each selected server
        test_results = []
        for config in selected_configs:
            update_progress(get_text('testing_connection', server=config['name']))
            success, message = test_server_connection(config)
            test_results.append((config['name'], success, message))

            # Update progress with result
            status = "✓" if success else "✗"
            update_progress(f"{status} {message}")
        # Show final summary
        update_progress(f"\n{get_text('test_summary')}")
        successful = sum(1 for _, success, _ in test_results if success)
        failed = len(test_results) - successful
        update_progress(get_text('successful', count=successful))
        update_progress(get_text('failed', count=failed))

        # Enable close button
        close_btn.configure(state="normal")

def preprocess_json_text(json_text):
    """
    Preprocess JSON text to handle common formatting issues.
    Args    :
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