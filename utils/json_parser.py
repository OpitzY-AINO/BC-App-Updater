def parse_server_config(config_data):
    """
    Parse the server configuration JSON data.

    Args:
        config_data (dict): Raw JSON configuration data

    Returns:
        list: List of server configurations

    Raises:
        ValueError: If the configuration format is invalid
    """
    if not isinstance(config_data, dict):
        raise ValueError("Configuration must be a JSON object")

    # Check for version field
    version = config_data.get('version')
    if not version:
        raise ValueError("Missing 'version' field in configuration")

    if 'configurations' not in config_data:
        raise ValueError("Missing 'configurations' field in configuration")

    configs = config_data['configurations']

    if not isinstance(configs, list):
        raise ValueError("'configurations' must be a list of server configurations")

    required_fields = [
        'name',
        'tenant',
        'environmentName',
        'environmentType'
    ]

    parsed_configs = []

    for i, config in enumerate(configs, 1):
        if not isinstance(config, dict):
            raise ValueError(f"Configuration {i} must be a JSON object")

        # Validate required fields
        missing_fields = [
            field for field in required_fields
            if field not in config
        ]

        if missing_fields:
            raise ValueError(
                f"Configuration {i} ({config.get('name', 'unnamed')}) "
                f"is missing required fields: {', '.join(missing_fields)}"
            )

        # Validate field types
        if not isinstance(config['name'], str):
            raise ValueError(f"Configuration {i}: 'name' must be a string")
        if not isinstance(config['tenant'], str):
            raise ValueError(f"Configuration {i}: 'tenant' must be a string")
        if not isinstance(config['environmentName'], str):
            raise ValueError(f"Configuration {i}: 'environmentName' must be a string")
        if not isinstance(config['environmentType'], str):
            raise ValueError(f"Configuration {i}: 'environmentType' must be a string")

        # Only include sandbox environments
        if config['environmentType'].lower() != 'sandbox':
            continue

        parsed_configs.append({
            'name': config['name'],
            'tenant': config['tenant'],
            'environmentName': config['environmentName'],
            'environmentType': config['environmentType'],
            'authentication': config.get('authentication', 'AAD'),
            'schemaUpdateMode': config.get('schemaUpdateMode', 'Synchronize')
        })

    return parsed_configs