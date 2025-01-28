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
    print(f"Starting to parse configuration data: {config_data}")

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

    parsed_configs = []
    print(f"Found {len(configs)} configurations to parse")

    for i, config in enumerate(configs, 1):
        print(f"Parsing configuration {i}: {config}")

        if not isinstance(config, dict):
            raise ValueError(f"Configuration {i} must be a JSON object")

        # Basic validation for required fields
        if 'name' not in config:
            raise ValueError(f"Configuration {i} is missing 'name' field")

        # Create base config with defaults
        parsed_config = {
            'name': config['name'],
            'type': config.get('type', 'al'),
            'request': config.get('request', 'launch'),
            'environmentType': config.get('environmentType', 'Sandbox'),
            'authentication': config.get('authentication', 'AAD')
        }

        # Add environment-specific fields
        env_type = config.get('environmentType', 'Sandbox').lower()

        if env_type == 'sandbox':
            parsed_config.update({
                'tenant': config.get('tenant', ''),
                'environmentName': config.get('environmentName', ''),
                'schemaUpdateMode': config.get('schemaUpdateMode', 'Synchronize'),
                'forceUpgrade': config.get('forceUpgrade', False)
            })
        elif env_type == 'onprem':
            parsed_config.update({
                'server': config.get('server', ''),
                'serverInstance': config.get('serverInstance', ''),
                'tenant': config.get('tenant', 'default'),
                'schemaUpdateMode': config.get('schemaUpdateMode', 'Synchronize'),
                'usePublicURLFromServer': config.get('usePublicURLFromServer', True)
            })

        print(f"Successfully parsed configuration {i}: {parsed_config}")
        parsed_configs.append(parsed_config)

    print(f"Successfully parsed {len(parsed_configs)} configurations")
    return parsed_configs