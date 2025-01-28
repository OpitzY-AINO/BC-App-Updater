def parse_server_config(config_data):
    """
    Parse the server configuration JSON data.

    Args:
        config_data (dict or list): Raw JSON configuration data

    Returns:
        list: List of server configurations

    Raises:
        ValueError: If the configuration format is invalid
    """
    # Handle list input (multiple configs)
    if isinstance(config_data, list):
        return [parse_single_config(config, i) for i, config in enumerate(config_data, 1)]

    # Handle dict input
    if not isinstance(config_data, dict):
        raise ValueError("Configuration must be a JSON object or array")

    # Check if this is a full configuration file format
    if 'version' in config_data and 'configurations' in config_data:
        configs = config_data['configurations']
        if not isinstance(configs, list):
            raise ValueError("'configurations' must be a list of server configurations")
        return [parse_single_config(config, i) for i, config in enumerate(configs, 1)]

    # If it's a single configuration (has name and type fields)
    if 'name' in config_data and 'environmentType' in config_data:
        return [parse_single_config(config_data)]

    raise ValueError("Invalid configuration format. Expected either a single configuration, "
                    "multiple configurations in an array, or a full configuration file format.")

def parse_single_config(config, index=1):
    """Parse a single server configuration.

    Args:
        config (dict): Single server configuration
        index (int): Configuration index for error messages

    Returns:
        dict: Parsed server configuration

    Raises:
        ValueError: If the configuration format is invalid
    """
    if not isinstance(config, dict):
        raise ValueError(f"Configuration {index} must be a JSON object")

    # Check environment type first
    if 'environmentType' not in config:
        raise ValueError(f"Configuration {index} ({config.get('name', 'unnamed')}) is missing 'environmentType' field")

    env_type = config['environmentType'].lower()

    # Basic validation for name
    if 'name' not in config:
        raise ValueError(f"Configuration {index} is missing 'name' field")

    # Create base config
    parsed_config = {
        'name': config['name'],
        'environmentType': config['environmentType'],
        'authentication': config.get('authentication', 'AAD')
    }

    # Add environment-specific fields
    if env_type == 'sandbox':
        # Validate required fields for sandbox
        if 'tenant' not in config:
            raise ValueError(f"Configuration {index} ({config['name']}) is missing 'tenant' field required for Sandbox environment")
        if 'environmentName' not in config:
            raise ValueError(f"Configuration {index} ({config['name']}) is missing 'environmentName' field required for Sandbox environment")

        parsed_config.update({
            'tenant': config['tenant'],
            'environmentName': config['environmentName'],
            'schemaUpdateMode': config.get('schemaUpdateMode', 'Synchronize')
        })
    elif env_type == 'onprem':
        # Validate required fields for onprem
        if 'server' not in config:
            raise ValueError(f"Configuration {index} ({config['name']}) is missing 'server' field required for OnPrem environment")
        if 'serverInstance' not in config:
            raise ValueError(f"Configuration {index} ({config['name']}) is missing 'serverInstance' field required for OnPrem environment")

        parsed_config.update({
            'server': config['server'],
            'serverInstance': config['serverInstance'],
            'tenant': config.get('tenant', 'default'),
            'schemaUpdateMode': config.get('schemaUpdateMode', 'Synchronize')
        })

    return parsed_config