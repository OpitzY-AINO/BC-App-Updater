import base64
import json
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import traceback
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CredentialManager:
    def __init__(self):
        """Initialize the credential manager."""
        self.credentials_file = "server_credentials.enc"
        try:
            logger.debug("Initializing credential manager")
            self._key = self._generate_key()
            self._fernet = Fernet(self._key)
            self._credentials = self._load_credentials()
            logger.debug("Credential manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize credential manager: {str(e)}\n{traceback.format_exc()}")
            self._credentials = {}
            # Remove potentially corrupted credentials file
            if os.path.exists(self.credentials_file):
                try:
                    os.remove(self.credentials_file)
                    logger.info("Removed corrupted credentials file")
                except Exception as remove_error:
                    logger.error(f"Failed to remove corrupted credentials file: {str(remove_error)}")

    def _generate_key(self):
        """Generate a secure encryption key"""
        try:
            logger.debug("Generating encryption key")

            # Use a static salt
            salt = b'BC_Publisher_Static_Salt'

            # Use a more stable machine identifier instead of just process ID
            # This ensures the same key is generated even across different runs
            machine_id = str(uuid.getnode()).encode()  # Uses MAC address for stability

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id))
            logger.debug("Encryption key generated successfully")
            return key
        except Exception as e:
            logger.error(f"Error generating encryption key: {str(e)}\n{traceback.format_exc()}")
            raise

    def _load_credentials(self):
        """Load encrypted credentials from file"""
        if not os.path.exists(self.credentials_file):
            logger.info(f"No credentials file found at {self.credentials_file}. Starting with empty credentials.")
            return {}

        try:
            logger.debug(f"Attempting to load credentials from {self.credentials_file}")
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    logger.warning("Credentials file is empty")
                    return {}

                logger.debug("Decrypting credentials data")
                try:
                    decrypted_data = self._fernet.decrypt(encrypted_data)
                    credentials = json.loads(decrypted_data)
                    logger.info(f"Successfully loaded credentials for {len(credentials)} servers")
                    return credentials
                except InvalidToken:
                    logger.error("Invalid token while decrypting credentials - file may be corrupted")
                    # Remove corrupted file
                    os.remove(self.credentials_file)
                    return {}

        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in credentials file: {str(e)}\n{traceback.format_exc()}")
            return {}
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}\n{traceback.format_exc()}")
            return {}

    def _save_credentials(self):
        """Save credentials to encrypted file"""
        try:
            logger.debug("Encrypting credentials data")
            encrypted_data = self._fernet.encrypt(json.dumps(self._credentials).encode())

            # Write to temporary file first
            temp_file = f"{self.credentials_file}.tmp"
            logger.debug(f"Writing encrypted data to temporary file: {temp_file}")
            with open(temp_file, 'wb') as f:
                f.write(encrypted_data)

            # Then rename to actual file (atomic operation)
            logger.debug(f"Moving temporary file to final location: {self.credentials_file}")
            os.replace(temp_file, self.credentials_file)
            logger.info("Successfully saved credentials")
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}\n{traceback.format_exc()}")
            # Remove temporary file if it exists
            if os.path.exists(f"{self.credentials_file}.tmp"):
                try:
                    logger.debug("Cleaning up temporary file")
                    os.remove(f"{self.credentials_file}.tmp")
                except:
                    pass
            raise

    def store_credentials(self, server_id, username, password):
        """Store credentials for a specific server"""
        try:
            logger.debug(f"Storing credentials for server: {server_id}")
            self._credentials[server_id] = {
                'username': username,
                'password': password
            }
            self._save_credentials()
            logger.info(f"Successfully stored credentials for server: {server_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credentials for {server_id}: {str(e)}\n{traceback.format_exc()}")
            return False

    def get_credentials(self, server_id):
        """Get credentials for a specific server"""
        creds = self._credentials.get(server_id)
        if creds:
            logger.info(f"Retrieved credentials for server: {server_id}")
        else:
            logger.info(f"No credentials found for server: {server_id}")
        return creds

    def remove_credentials(self, server_id):
        """Remove credentials for a specific server"""
        try:
            if server_id in self._credentials:
                logger.debug(f"Removing credentials for server: {server_id}")
                del self._credentials[server_id]
                self._save_credentials()
                logger.info(f"Successfully removed credentials for server: {server_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing credentials for {server_id}: {str(e)}\n{traceback.format_exc()}")
            return False

    def clear_all_credentials(self):
        """Clear all stored credentials"""
        try:
            logger.debug("Clearing all credentials")
            self._credentials = {}
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
            logger.info("Successfully cleared all credentials")
            return True
        except Exception as e:
            logger.error(f"Error clearing credentials: {str(e)}\n{traceback.format_exc()}")
            return False