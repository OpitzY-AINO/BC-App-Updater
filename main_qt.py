import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QFrame, QTreeWidget, QTreeWidgetItem,
                            QMessageBox, QScrollArea, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from utils.config_manager import ConfigurationManager
from utils.credential_manager import CredentialManager
from utils.json_parser import parse_server_config
from utils.app_publisher import AppPublisher
from utils.translations import get_text

class PublishWorker(QThread):
    progress = pyqtSignal(str, bool, str)  # server_name, success, message
    finished = pyqtSignal()
    credential_request = pyqtSignal(dict)
    credential_response = None

    def __init__(self, app_file_path, configs, credential_manager):
        super().__init__()
        self.app_file_path = app_file_path
        self.configs = configs
        self.credential_manager = credential_manager

    def run(self):
        for config in self.configs:
            if config['environmentType'].lower() == 'onprem':
                server_id = f"{config['server']}_{config['serverInstance']}"
                
                # Try to get existing credentials
                existing_creds = self.credential_manager.get_credentials(server_id)
                if existing_creds:
                    username = existing_creds['username']
                    password = existing_creds['password']
                else:
                    # Request credentials from main thread
                    self.credential_request.emit(config)
                    while self.credential_response is None:
                        self.msleep(100)
                    
                    if not self.credential_response:
                        self.progress.emit(config['name'], False, "No credentials provided")
                        continue
                        
                    username = self.credential_response['username']
                    password = self.credential_response['password']
                    self.credential_response = None

                success, message = AppPublisher.publish_to_onprem(
                    self.app_file_path,
                    config,
                    username,
                    password
                )

                if success:
                    self.credential_manager.store_credentials(server_id, username, password)

                self.progress.emit(config['name'], success, message)

        self.finished.emit()

class DropZone(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self, accept_extensions, placeholder_text):
        super().__init__()
        self.accept_extensions = accept_extensions
        self.setFrameStyle(QFrame.Shape.Box)
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout()
        self.label = QLabel(placeholder_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if any(file_path.lower().endswith(ext) for ext in self.accept_extensions):
                event.accept()
            else:
                event.ignore()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.fileDropped.emit(file_path)

    def update_text(self, text):
        self.label.setText(text)

class BCPublisherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_text('app_title'))
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)

        self.app_file_path = None
        self.config_manager = ConfigurationManager()
        self.credential_manager = CredentialManager()

        self.setup_ui()
        self.update_server_list()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # App Drop Zone
        self.app_drop_zone = DropZone(['.app'], get_text('drop_app'))
        self.app_drop_zone.fileDropped.connect(self.handle_app_drop)
        layout.addWidget(self.app_drop_zone)

        # Config Drop Zone
        self.config_drop_zone = DropZone(['.json'], get_text('drop_json'))
        self.config_drop_zone.fileDropped.connect(self.handle_config_drop)
        layout.addWidget(self.config_drop_zone)

        # Server List
        self.server_tree = QTreeWidget()
        self.server_tree.setHeaderLabels([
            get_text('col_select'),
            get_text('col_type'),
            get_text('col_name'),
            get_text('col_environment')
        ])
        self.server_tree.itemClicked.connect(self.handle_server_click)
        layout.addWidget(self.server_tree)

        # Buttons
        button_layout = QVBoxLayout()
        
        self.test_connection_btn = QPushButton(get_text('test_connection'))
        self.test_connection_btn.clicked.connect(self.test_selected_connections)
        self.test_connection_btn.setEnabled(False)
        button_layout.addWidget(self.test_connection_btn)

        self.publish_button = QPushButton(get_text('publish_button'))
        self.publish_button.clicked.connect(self.publish_extension)
        self.publish_button.setEnabled(False)
        button_layout.addWidget(self.publish_button)

        layout.addLayout(button_layout)

    def handle_app_drop(self, file_path):
        if file_path.lower().endswith('.app'):
            self.app_file_path = file_path
            self.app_drop_zone.update_text(f"Selected: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, "Error", get_text('invalid_app'))

    def handle_config_drop(self, file_path):
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
                new_configs = parse_server_config(config_data)
                self.config_manager.add_configurations(new_configs)
                self.update_server_list()
                self.config_drop_zone.update_text(f"Loaded {len(new_configs)} server configurations")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_server_list(self):
        self.server_tree.clear()
        for config in self.config_manager.get_configurations():
            item = QTreeWidgetItem()
            item.setText(0, "☐")
            item.setText(1, config['environmentType'])
            item.setText(2, config['name'])
            item.setText(3, config['serverInstance'])
            self.server_tree.addTopLevelItem(item)

    def handle_server_click(self, item, column):
        if column == 0:  # Checkbox column
            item.setText(0, "☑" if item.text(0) == "☐" else "☐")
            self.update_button_states()

    def update_button_states(self):
        has_selection = any(
            item.text(0) == "☑"
            for i in range(self.server_tree.topLevelItemCount())
            for item in [self.server_tree.topLevelItem(i)]
        )
        self.publish_button.setEnabled(has_selection)
        self.test_connection_btn.setEnabled(has_selection)

    def get_selected_configs(self):
        selected_configs = []
        for i in range(self.server_tree.topLevelItemCount()):
            item = self.server_tree.topLevelItem(i)
            if item.text(0) == "☑":
                config = self.config_manager.get_configurations()[i]
                selected_configs.append(config)
        return selected_configs

    def show_progress_dialog(self):
        dialog = QWidget(self)
        dialog.setWindowTitle(get_text('deployment_progress'))
        layout = QVBoxLayout(dialog)

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        layout.addWidget(self.progress_text)

        dialog.resize(800, 600)
        dialog.show()
        return dialog

    def publish_extension(self):
        if not self.app_file_path:
            QMessageBox.critical(self, "Error", get_text('select_app'))
            return

        selected_configs = self.get_selected_configs()
        if not selected_configs:
            QMessageBox.critical(self, "Error", get_text('select_server'))
            return

        # Show progress dialog
        progress_dialog = self.show_progress_dialog()

        # Create and start worker thread
        self.publish_worker = PublishWorker(
            self.app_file_path,
            selected_configs,
            self.credential_manager
        )

        def handle_progress(server_name, success, message):
            status = "✓" if success else "✗"
            self.progress_text.append(f"{status} {server_name}: {message}")

        def handle_credential_request(config):
            # Show credential dialog and send response back to worker
            from utils.credential_dialog import get_credentials
            credentials = get_credentials(self, config)
            self.publish_worker.credential_response = credentials

        self.publish_worker.progress.connect(handle_progress)
        self.publish_worker.credential_request.connect(handle_credential_request)
        self.publish_worker.start()

def main():
    app = QApplication(sys.argv)
    window = BCPublisherApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
