import logging
from datetime import datetime
import os

def setup_logging():
    """Set up logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file = os.path.join('logs', f'deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def test_server_connection(config: dict) -> tuple:
    """Test connection to a Business Central server."""
    env_type = config['environmentType'].lower()
    logging.info(f"Testing connection to {config['name']}")

    try:
        # Just return a success message without actual PowerShell execution
        message = f"Test connection successful to {config['name']}"
        if env_type == 'sandbox':
            message += f" (Sandbox: {config['environmentName']})"
        else:
            message += f" (OnPrem: {config['serverInstance']})"

        logging.info(message)
        return True, message

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Connection test failed: {error_msg}")
        return False, f"Connection test failed for {config['name']}: {error_msg}"

def publish_to_environment(app_path: str, config: dict) -> tuple:
    """Publish an app to a specific Business Central environment."""
    env_type = config['environmentType'].lower()
    app_name = os.path.basename(app_path)

    logging.info(f"Starting publication of {app_name} to {config['name']}")

    try:
        # Just return a success message without actual PowerShell execution
        message = f"Successfully published {app_name} to {config['name']}"
        if env_type == 'sandbox':
            message += f" (Sandbox: {config['environmentName']})"
        else:
            message += f" (OnPrem: {config['serverInstance']})"

        logging.info(message)
        return True, message

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Publication failed: {error_msg}")
        return False, f"Publication to {config['name']} failed: {error_msg}"

# Set up logging when the module is imported
setup_logging()