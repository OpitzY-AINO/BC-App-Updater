from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt

def get_credentials(parent, server_config):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Server Authentication")
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    dialog.resize(400, 300)

    layout = QVBoxLayout(dialog)

    # Header
    header = QLabel(f"Authentication Required\n{server_config['name']}")
    header.setStyleSheet("font-size: 14pt; font-weight: bold;")
    header.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(header)

    # Username
    username_label = QLabel("Username")
    layout.addWidget(username_label)
    username_entry = QLineEdit()
    layout.addWidget(username_entry)

    # Password
    password_label = QLabel("Password")
    layout.addWidget(password_label)
    password_entry = QLineEdit()
    password_entry.setEchoMode(QLineEdit.EchoMode.Password)
    layout.addWidget(password_entry)

    # Buttons
    button_layout = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    connect_btn = QPushButton("Connect")
    button_layout.addWidget(cancel_btn)
    button_layout.addWidget(connect_btn)
    layout.addLayout(button_layout)

    result = {'username': None, 'password': None}

    def on_ok():
        result['username'] = username_entry.text()
        result['password'] = password_entry.text()
        dialog.accept()

    def on_cancel():
        dialog.reject()

    # Connect signals
    cancel_btn.clicked.connect(on_cancel)
    connect_btn.clicked.connect(on_ok)

    # Handle Enter key in password field
    def handle_return_key(event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            on_ok()
            return True
        return False

    password_entry.keyPressEvent = handle_return_key
    username_entry.returnPressed.connect(lambda: password_entry.setFocus())

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return result
    return None