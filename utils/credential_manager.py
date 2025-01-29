import base64
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

class CredentialManager:
    def __init__(self):
        self.credentials_file = "server_credentials.enc"
        self._key = self._generate_key()
        self._fernet = Fernet(self._key)
        self._credentials = self._load_credentials()

    def _generate_key(self):
        """Generate a secure encryption key"""
        # Use a static salt - while not ideal, it's better than storing plaintext
        salt = b'BC_Publisher_Static_Salt'
        # Use machine-specific data as password
        machine_specific = str(os.getpid()).encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_specific))
        return key

    def _load_credentials(self):
        """Load encrypted credentials from file"""
        if not os.path.exists(self.credentials_file):
            return {}
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self._fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data)
        except Exception as e:
            logging.error(f"Error loading credentials: {str(e)}")
            return {}

    def _save_credentials(self):
        """Save credentials to encrypted file"""
        try:
            encrypted_data = self._fernet.encrypt(json.dumps(self._credentials).encode())
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logging.error(f"Error saving credentials: {str(e)}")

    def store_credentials(self, server_id, username, password):
        """Store credentials for a specific server"""
        self._credentials[server_id] = {
            'username': username,
            'password': password
        }
        self._save_credentials()

    def get_credentials(self, server_id):
        """Get credentials for a specific server"""
        return self._credentials.get(server_id, None)

    def remove_credentials(self, server_id):
        """Remove credentials for a specific server"""
        if server_id in self._credentials:
            del self._credentials[server_id]
            self._save_credentials()

    def clear_all_credentials(self):
        """Clear all stored credentials"""
        self._credentials = {}
        if os.path.exists(self.credentials_file):
            try:
                os.remove(self.credentials_file)
            except Exception as e:
                logging.error(f"Error removing credentials file: {str(e)}")
