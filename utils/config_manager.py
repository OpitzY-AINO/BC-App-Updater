import json
import os
from typing import List, Dict, Optional
import tkinter.messagebox as messagebox
from .translations import get_text

class ConfigurationManager:
    def __init__(self, config_file: str = "saved_configurations.json"):
        """Initialize the configuration manager with a storage file path."""
        self.config_file = config_file
        self.configurations: List[Dict] = []
        self.load_configurations()

    def load_configurations(self) -> None:
        """Load saved configurations from file if it exists."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.configurations = json.load(f)
        except Exception as e:
            print(f"Error loading configurations: {e}")
            self.configurations = []

    def save_configurations(self) -> None:
        """Save current configurations to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.configurations, f, indent=2)
        except Exception as e:
            print(f"Error saving configurations: {e}")

    def find_config_by_name(self, name: str) -> Optional[Dict]:
        """Find a configuration by its name."""
        return next((config for config in self.configurations if config['name'] == name), None)

    def add_configurations(self, new_configs: List[Dict], ask_overwrite: bool = True) -> None:
        """
        Add new configurations to the existing ones.

        Args:
            new_configs: List of new configurations to add
            ask_overwrite: Whether to ask for confirmation before overwriting existing configs
        """
        for new_config in new_configs:
            existing_config = self.find_config_by_name(new_config['name'])

            if existing_config:
                if ask_overwrite:
                    # Ask user for confirmation with translated message
                    if messagebox.askyesno(
                        "Configuration Exists",
                        get_text('config_exists', name=new_config['name'])
                    ):
                        # Replace existing configuration
                        idx = self.configurations.index(existing_config)
                        self.configurations[idx] = new_config
                    # If user says no, skip this configuration
                else:
                    # Replace without asking when ask_overwrite is False
                    idx = self.configurations.index(existing_config)
                    self.configurations[idx] = new_config
            else:
                # Add new configuration
                self.configurations.append(new_config)

        # Save after modifications
        self.save_configurations()

    def replace_configurations(self, new_configs: List[Dict]) -> None:
        """
        Replace all configurations with new ones.
        Used when editing configurations in the editor.

        Args:
            new_configs: List of new configurations to replace existing ones
        """
        self.configurations = new_configs
        self.save_configurations()

    def clear_configurations(self) -> None:
        """Clear all configurations and save empty state."""
        self.configurations = []
        self.save_configurations()

    def get_configurations(self) -> List[Dict]:
        """Get current configurations."""
        return self.configurations.copy()