import os
import requests
from urllib.parse import urljoin
from base64 import b64encode

class AppPublisher:
    DEFAULT_PORT = "7049"

    @staticmethod
    def _create_auth_header(username, password):
        """Create Basic Auth header from credentials"""
        credentials = f"{username}:{password}"
        encoded = b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    @staticmethod
    def _create_publish_url(server, instance, tenant):
        """Create the publishing URL for Business Central"""
        base_url = f"http://{server}:{AppPublisher.DEFAULT_PORT}/{instance}"
        path = f"dev/apps"
        params = {
            'tenant': tenant,
            'SchemaUpdateMode': 'forcesync',
            'DependencyPublishingOption': 'default'
        }

        # Construct URL with parameters
        url = urljoin(base_url, path)
        param_str = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{url}?{param_str}"

    @staticmethod
    def publish_to_onprem(app_path, config, username, password):
        """
        Publish an app to an on-premises Business Central server

        Args:
            app_path: Path to the .app file
            config: Server configuration dictionary
            username: Server credentials username
            password: Server credentials password

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not os.path.exists(app_path):
                return False, f"App file not found: {app_path}"

            url = AppPublisher._create_publish_url(
                config['server'],
                config['serverInstance'],
                config.get('tenant', 'default')
            )

            headers = {
                'Authorization': AppPublisher._create_auth_header(username, password)
            }

            # Prepare the file for upload
            app_name = os.path.basename(app_path)
            with open(app_path, 'rb') as f:
                files = {'file': (app_name, f)}
                response = requests.post(url, headers=headers, files=files)

            if response.ok:
                message = f"Successfully published {app_name} to {config['name']}"
                return True, message
            else:
                # Try to get detailed error message from response
                try:
                    error_details = response.json().get('Message', response.text)
                except:
                    error_details = response.text

                error_msg = f"Publishing failed (Status {response.status_code}): {error_details}"
                return False, error_msg

        except Exception as e:
            error_msg = f"Error publishing app: {str(e)}"
            return False, error_msg