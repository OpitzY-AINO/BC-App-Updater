import subprocess
import sys
import tempfile
import os

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
