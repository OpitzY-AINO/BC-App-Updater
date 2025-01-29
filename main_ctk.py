import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import json
from typing import Optional, List, Dict
import threading
from queue import Queue, Empty
import logging
from datetime import datetime, timedelta
import traceback

from utils.config_manager import ConfigurationManager
from utils.credential_manager import CredentialManager
from utils.json_parser import parse_server_config
from utils.app_publisher import AppPublisher
from utils.translations import get_text

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DropFrame(ctk.CTkFrame):
    def __init__(self, master, title: str, accept_extensions: List[str], placeholder: str, **kwargs):
        super().__init__(master, **kwargs)

        self.accept_extensions = accept_extensions
        self.file_path = None

        # Enable DND
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._handle_drop)

        # Header
        self.title_label = ctk.CTkLabel(self, text=title, font=("Segoe UI", 14, "bold"))
        self.title_label.pack(pady=(10, 5))

        # Drop area
        self.drop_label = ctk.CTkLabel(
            self,
            text=placeholder,
            height=60,
            fg_color=("gray85", "gray25"),
            corner_radius=8
        )
        self.drop_label.pack(pady=10, padx=20, fill="x", expand=True)

        # Configure drag and drop visual feedback
        self.drop_label.configure(cursor="hand2")
        self.drop_label.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        """Handle click to open file dialog"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[(f"{ext.upper()} files", f"*{ext}") for ext in self.accept_extensions]
        )
        if file_path:
            self._process_file(file_path)

    def _handle_drop(self, event):
        """Handle file drop"""
        file_path = event.data
        if file_path.startswith('{'):
            file_path = file_path[1:-1]  # Remove curly braces if present
        self._process_file(file_path)
        return "break"

    def _process_file(self, file_path: str):
        """Process the dropped/selected file"""
        if any(file_path.lower().endswith(ext) for ext in self.accept_extensions):
            self.file_path = file_path
            self.drop_label.configure(text=f"Selected: {os.path.basename(file_path)}")
            return True
        return False

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

                    # Try to get existing credentials
                    existing_creds = self.credential_manager.get_credentials(server_id)
                    if existing_creds:
                        logger.debug(f"Using existing credentials for {server_id}")
                        username = existing_creds['username']
                        password = existing_creds['password']
                    else:
                        # Request credentials from main thread
                        logger.debug(f"Requesting credentials for {server_id}")
                        self.result_queue.put(('need_credentials', server_id, config))

                        # Wait for credentials response with timeout
                        try:
                            logger.debug(f"Waiting for credentials for {server_id}")
                            response = self.result_queue.get(timeout=60)
                            if response[0] != 'credentials_provided':
                                logger.warning(f"No credentials provided for {server_id}")
                                self.result_queue.put(('failed', config['name'], "No credentials provided"))
                                continue
                            username = response[1]
                            password = response[2]
                        except Empty:
                            logger.error(f"Timeout waiting for credentials for {server_id}")
                            self.result_queue.put(('failed', config['name'], "Credential request timed out"))
                            continue

                    try:
                        logger.debug(f"Publishing to {server_id}")
                        success, message = AppPublisher.publish_to_onprem(
                            self.app_file_path,
                            config,
                            username,
                            password
                        )

                        if success:
                            logger.debug(f"Successfully published to {server_id}, storing credentials")
                            self.credential_manager.store_credentials(server_id, username, password)
                        else:
                            logger.warning(f"Failed to publish to {server_id}: {message}")

                        self.result_queue.put(('progress', config['name'], success, message))
                    except Exception as e:
                        logger.error(f"Error publishing to {server_id}: {str(e)}\n{traceback.format_exc()}")
                        self.result_queue.put(('failed', config['name'], f"Error: {str(e)}"))

        except Exception as e:
            logger.error(f"Worker thread error: {str(e)}\n{traceback.format_exc()}")
            self.result_queue.put(('error', str(e)))

class BCPublisherApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title(get_text('app_title'))
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Set color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize managers
        self.config_manager = ConfigurationManager()
        self.credential_manager = CredentialManager()

        # Setup UI
        self.setup_ui()
        self.update_server_list()

    def setup_ui(self):
        # Main container with padding
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # App drop zone
        self.app_drop = DropFrame(
            container,
            title=get_text('extension_file'),
            accept_extensions=['.app'],
            placeholder=get_text('drop_app'),
            height=100
        )
        self.app_drop.pack(fill="x", pady=(0, 10))

        # Config drop zone
        self.config_drop = DropFrame(
            container,
            title=get_text('server_config'),
            accept_extensions=['.json'],
            placeholder=get_text('drop_json'),
            height=100
        )
        self.config_drop.pack(fill="x", pady=(0, 10))

        # Server list frame
        list_frame = ctk.CTkFrame(container)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Server list with scrollable frame
        self.tree = ctk.CTkScrollableFrame(list_frame)
        self.tree.pack(fill="both", expand=True)

        # Action buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=(0, 10))

        self.test_btn = ctk.CTkButton(
            button_frame,
            text=get_text('test_connection'),
            command=self.test_selected_connections,
            state="disabled"
        )
        self.test_btn.pack(side="left", padx=5)

        self.publish_btn = ctk.CTkButton(
            button_frame,
            text=get_text('publish_button'),
            command=self.publish_extension,
            state="disabled"
        )
        self.publish_btn.pack(side="right", padx=5)

    def update_server_list(self):
        # Clear existing items
        for widget in self.tree.winfo_children():
            widget.destroy()

        # Add items from configuration manager
        for i, config in enumerate(self.config_manager.get_configurations()):
            row = ctk.CTkFrame(self.tree)
            row.pack(fill="x", pady=2)

            # Checkbox
            var = ctk.BooleanVar()
            check = ctk.CTkCheckBox(row, text="", variable=var, width=40)
            check.pack(side="left", padx=5)

            # Labels
            ctk.CTkLabel(row, text=config['environmentType'], width=100).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=config['name'], width=200).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=config.get('serverInstance', ''), width=200).pack(side="left", padx=5)

    def show_credential_dialog(self, server_config):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Server Authentication")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Header
        header = ctk.CTkLabel(
            dialog,
            text=f"Authentication Required\n{server_config['name']}",
            font=("Segoe UI", 14, "bold")
        )
        header.pack(pady=20)

        # Username
        username_label = ctk.CTkLabel(dialog, text="Username")
        username_label.pack(pady=(10, 0))
        username_entry = ctk.CTkEntry(dialog)
        username_entry.pack(pady=(0, 10), padx=20, fill="x")

        # Password
        password_label = ctk.CTkLabel(dialog, text="Password")
        password_label.pack(pady=(10, 0))
        password_entry = ctk.CTkEntry(dialog, show="•")
        password_entry.pack(pady=(0, 20), padx=20, fill="x")

        result = {'username': None, 'password': None}

        def on_ok():
            result['username'] = username_entry.get()
            result['password'] = password_entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Connect",
            command=on_ok,
            width=100
        ).pack(side="right", padx=5)

        # Center dialog on parent window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()
        return result['username'], result['password']

    def test_selected_connections(self):
        """Test connection to selected servers"""
        selected_servers = []
        for widget in self.tree.winfo_children():
            checkbox = widget.winfo_children()[0]  # First child is the checkbox
            if isinstance(checkbox, ctk.CTkCheckBox) and checkbox.get():
                index = list(self.tree.winfo_children()).index(widget)
                if 0 <= index < len(self.config_manager.get_configurations()):
                    selected_servers.append(self.config_manager.get_configurations()[index])

        if not selected_servers:
            from tkinter import messagebox
            messagebox.showerror("Error", get_text('select_server_test'))
            return

        # Create a progress dialog
        progress_dialog = self.show_progress_dialog(get_text('connection_test_progress'))
        progress_text = progress_dialog.winfo_children()[0]  # First child is the text widget

        for config in selected_servers:
            progress_text.insert('end', f"Testing connection to {config['name']}...\n")
            progress_text.see('end')
            progress_text.update()

            success, message = AppPublisher.test_server_connection(config)
            status = "✓" if success else "✗"
            progress_text.insert('end', f"{status} {message}\n")
            progress_text.see('end')
            progress_text.update()

    def show_progress_dialog(self, title):
        """Create and show a progress dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()

        # Text widget for progress
        text = ctk.CTkTextbox(dialog)
        text.pack(fill="both", expand=True, padx=20, pady=20)

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        return dialog

    def publish_extension(self):
        """Handle publishing extension to selected servers"""
        if not self.app_drop.file_path:
            from tkinter import messagebox
            messagebox.showerror("Error", get_text('select_app'))
            return

        selected_servers = []
        for widget in self.tree.winfo_children():
            checkbox = widget.winfo_children()[0]  # First child is the checkbox
            if isinstance(checkbox, ctk.CTkCheckBox) and checkbox.get():
                index = list(self.tree.winfo_children()).index(widget)
                if 0 <= index < len(self.config_manager.get_configurations()):
                    selected_servers.append(self.config_manager.get_configurations()[index])

        if not selected_servers:
            from tkinter import messagebox
            messagebox.showerror("Error", get_text('select_server'))
            return

        # Show progress dialog
        progress_dialog = self.show_progress_dialog(get_text('deployment_progress'))
        progress_text = progress_dialog.winfo_children()[0]

        def update_progress(message):
            progress_text.insert('end', f"{message}\n")
            progress_text.see('end')
            progress_text.update()

        # Initialize worker thread
        result_queue = Queue()
        worker = PublishWorker(
            self.app_drop.file_path,
            selected_servers,
            self.credential_manager,
            result_queue
        )

        def check_progress():
            try:
                while True:
                    try:
                        result = result_queue.get_nowait()
                        if result[0] == 'need_credentials':
                            server_id, config = result[1], result[2]
                            username, password = self.show_credential_dialog(config)
                            if username and password:
                                result_queue.put(('credentials_provided', username, password))
                            else:
                                result_queue.put(('credentials_failed',))
                        elif result[0] == 'progress':
                            server_name, success, message = result[1], result[2], result[3]
                            status = "✓" if success else "✗"
                            update_progress(f"{status} {server_name}: {message}")
                        elif result[0] == 'error':
                            update_progress(f"Error: {result[1]}")
                            break
                    except Empty:
                        break

                if worker.is_alive():
                    self.after(100, check_progress)
            except Exception as e:
                update_progress(f"Error checking progress: {str(e)}")

        worker.start()
        check_progress()

def main():
    app = BCPublisherApp()
    app.mainloop()

if __name__ == "__main__":
    main()