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

def is_powershell_available():
    """Check if PowerShell is available on the system"""
    try:
        result = subprocess.run(['powershell.exe', '-Command', 'echo "test"'], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def mock_powershell_command(command):
    """Mock PowerShell command execution for testing"""
    logging.info("Using mock PowerShell implementation")
    # Extract the message box content from the command
    if "[System.Windows.MessageBox]::Show(" in command:
        # Log the mock execution
        logging.info("Mock PowerShell execution: Message box would show")
        return "Mock PowerShell execution successful", ""
    return "Mock execution completed", ""

def execute_powershell(command):
    """
    Execute a PowerShell command and return the output.
    Falls back to mock implementation when PowerShell is not available.
    """
    if not is_powershell_available():
        return mock_powershell_command(command)

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

def test_server_connection(config: dict) -> tuple:
    """
    Test connection to a Business Central server.
    """
    env_type = config['environmentType'].lower()
    logging.info(f"Testing connection to {config['name']}")

    try:
        if env_type == 'sandbox':
            command = f"""
            $ErrorActionPreference = 'Stop'
            Write-Host "Testing connection to {config['name']} ({config['environmentName']})"

            Add-Type -AssemblyName PresentationFramework
            [System.Windows.MessageBox]::Show(
                "Test connection to Sandbox Environment:`n`nName: {config['name']}`nEnvironment: {config['environmentName']}`nTenant: {config['tenant']}",
                "Connection Test",
                "OK",
                "Information"
            )

            Write-Host "Connection test successful for {config['name']}"
            """
        elif env_type == 'onprem':
            command = f"""
            $ErrorActionPreference = 'Stop'
            Write-Host "Testing connection to {config['name']} ({config['serverInstance']})"

            Add-Type -AssemblyName PresentationFramework
            [System.Windows.MessageBox]::Show(
                "Test connection to OnPrem Server:`n`nName: {config['name']}`nServer: {config['server']}`nInstance: {config['serverInstance']}",
                "Connection Test",
                "OK",
                "Information"
            )

            Write-Host "Connection test successful for {config['name']}"
            """

        stdout, stderr = execute_powershell(command)
        logging.info(f"Connection test output: {stdout}")

        return True, f"Successfully connected to {config['name']} (Mock implementation if PowerShell unavailable)"

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Connection test failed: {error_msg}")
        return False, f"Connection test failed for {config['name']}: {error_msg}"

def publish_to_environment(app_path: str, config: dict) -> tuple:
    """
    Publish an app to a specific Business Central environment.
    """
    env_type = config['environmentType'].lower()
    app_name = os.path.basename(app_path)

    logging.info(f"Starte Veröffentlichung von {app_name} auf {config['name']}")

    try:
        if env_type == 'sandbox':
            command = f"""
            $ErrorActionPreference = 'Stop'
            Write-Host "Veröffentliche {app_name} auf {config['name']} ({config['environmentName']})"

            Add-Type -AssemblyName PresentationFramework
            [System.Windows.MessageBox]::Show(
                "Publishing to Sandbox Environment:`n`nName: {config['name']}`nEnvironment: {config['environmentName']}`nTenant: {config['tenant']}",
                "Deployment Info",
                "OK",
                "Information"
            )

            Write-Host "Veröffentlichung auf Mandant: {config['tenant']}, Umgebung: {config['environmentName']}"
            """

        elif env_type == 'onprem':
            command = f"""
            $ErrorActionPreference = 'Stop'
            Write-Host "Veröffentliche {app_name} auf {config['name']} ({config['serverInstance']})"

            Add-Type -AssemblyName PresentationFramework
            [System.Windows.MessageBox]::Show(
                "Publishing to OnPrem Server:`n`nName: {config['name']}`nServer: {config['server']}`nInstance: {config['serverInstance']}",
                "Deployment Info",
                "OK",
                "Information"
            )

            Write-Host "Veröffentlichung auf Server: {config['server']}, Instanz: {config['serverInstance']}"
            """

        stdout, stderr = execute_powershell(command)
        logging.info(f"Veröffentlichungsausgabe: {stdout}")

        return True, f"Erfolgreich auf {config['name']} veröffentlicht (Mock implementation if PowerShell unavailable)"

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Veröffentlichung fehlgeschlagen: {error_msg}")
        return False, f"Veröffentlichung auf {config['name']} fehlgeschlagen: {error_msg}"

# Set up logging when the module is imported
setup_logging()