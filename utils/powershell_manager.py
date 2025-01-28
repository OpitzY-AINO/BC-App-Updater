import subprocess
import sys
import tempfile
import os
import logging
from datetime import datetime

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

def publish_to_environment(app_path: str, config: dict) -> tuple:
    """
    Publish an app to a specific Business Central environment.

    Args:
        app_path (str): Path to the .app file
        config (dict): Server configuration dictionary

    Returns:
        tuple: (success: bool, message: str)
    """
    env_type = config['environmentType'].lower()
    app_name = os.path.basename(app_path)

    # Log deployment attempt in German
    logging.info(f"Starte Veröffentlichung von {app_name} auf {config['name']}")

    try:
        if env_type == 'sandbox':
            command = f"""
            $ErrorActionPreference = 'Stop'
            Write-Host "Veröffentliche {app_name} auf {config['name']} ({config['environmentName']})"

            # TODO: Replace with actual deployment commands
            $tenant = "{config['tenant']}"
            $environment = "{config['environmentName']}"
            $appPath = "{app_path}"

            Write-Host "Veröffentlichung auf Mandant: $tenant, Umgebung: $environment"
            """

        elif env_type == 'onprem':
            command = f"""
            $ErrorActionPreference = 'Stop'
            Write-Host "Veröffentliche {app_name} auf {config['name']} ({config['serverInstance']})"

            # TODO: Replace with actual deployment commands
            $server = "{config['server']}"
            $instance = "{config['serverInstance']}"
            $appPath = "{app_path}"

            Write-Host "Veröffentlichung auf Server: $server, Instanz: $instance"
            """

        stdout, stderr = execute_powershell(command)
        logging.info(f"Veröffentlichungsausgabe: {stdout}")

        if stderr:
            logging.error(f"Veröffentlichungsfehler: {stderr}")
            return False, f"Veröffentlichung auf {config['name']} fehlgeschlagen: {stderr}"

        return True, f"Erfolgreich auf {config['name']} veröffentlicht"

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Veröffentlichung fehlgeschlagen: {error_msg}")
        return False, f"Veröffentlichung auf {config['name']} fehlgeschlagen: {error_msg}"

def execute_powershell(command):
    """
    Execute a PowerShell command and return the output.

    Args:
        command (str): PowerShell command to execute

    Returns:
        tuple: (stdout, stderr)

    Raises:
        subprocess.CalledProcessError: If the command execution fails
    """
    # Create a temporary file for the PowerShell script
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ps1', mode='w') as script_file:
        script_file.write(command)
        script_path = script_file.name

    try:
        # Execute PowerShell with the script
        process = subprocess.Popen(
            [
                'powershell.exe',
                '-NoProfile',
                '-NonInteractive',
                '-ExecutionPolicy', 'Bypass',
                '-File', script_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                'powershell.exe',
                stdout,
                stderr
            )

        return stdout, stderr

    finally:
        # Clean up the temporary script file
        try:
            os.unlink(script_path)
        except:
            pass

# Set up logging when the module is imported
setup_logging()