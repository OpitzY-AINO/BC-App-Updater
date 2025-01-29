import os
import requests
from urllib.parse import urljoin, urlparse
from base64 import b64encode
from utils.powershell_manager import publish_to_environment, test_server_connection

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
        parsed_url = urlparse(server)
        if parsed_url.scheme:
            base_url = f"{parsed_url.scheme}://{parsed_url.hostname}:{AppPublisher.DEFAULT_PORT}/{instance}/"
        else:
            base_url = f"http://{server}:{AppPublisher.DEFAULT_PORT}/{instance}/"

        path = f"dev/apps"
        params = {
            'tenant': tenant,
            'SchemaUpdateMode': 'forcesync',
            'DependencyPublishingOption': 'default'
        }

        url = urljoin(base_url, path)
        param_str = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{url}?{param_str}"

    @staticmethod
    def publish_to_onprem(app_path, config, username=None, password=None):
        """
        Publish an app to an on-premises Business Central server
        """
        return publish_to_environment(app_path, config, username, password)

    @staticmethod
    def test_server_connection(config):
        """Test connection to a Business Central server."""
        return test_server_connection(config)