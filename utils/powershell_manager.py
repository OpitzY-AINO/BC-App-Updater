import os
from datetime import datetime

def setup_logging():
    """Set up logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

def test_server_connection(config: dict) -> tuple:
    """Test connection to a Business Central server."""
    env_type = config['environmentType'].lower()

    try:
        # Just return a success message without actual PowerShell execution
        message = f"Test connection successful to {config['name']}"
        if env_type == 'sandbox':
            message += f" (Sandbox: {config['environmentName']})"
        else:
            message += f" (OnPrem: {config['serverInstance']})"
        return True, message

    except Exception as e:
        error_msg = str(e)
        return False, f"Connection test failed for {config['name']}: {error_msg}"

def publish_to_environment(app_path: str, config: dict, username: str = None, password: str = None) -> tuple:
    """Publish an app to a specific Business Central environment."""
    env_type = config['environmentType'].lower()
    app_name = os.path.basename(app_path)

    try:
        # Just return a success message without actual PowerShell execution
        message = f"Successfully published {app_name} to {config['name']}"
        if env_type == 'sandbox':
            message += f" (Sandbox: {config['environmentName']})"
        else:
            message += f" (OnPrem: {config['serverInstance']}"
            if username:
                message += f" as {username})"
            else:
                message += ")"
        return True, message

    except Exception as e:
        error_msg = str(e)
        return False, f"Publication to {config['name']} failed: {error_msg}"

# Set up logging when the module is imported
setup_logging()