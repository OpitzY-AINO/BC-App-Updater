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
        raise ValueError("Invalid configuration format")
        
    if 'configurations' not in config_data:
        raise ValueError("Missing 'configurations' in config file")
        
    configs = config_data['configurations']
    
    if not isinstance(configs, list):
        raise ValueError("'configurations' must be a list")
        
    required_fields = [
        'name',
        'tenant',
        'environmentName',
        'environmentType'
    ]
    
    parsed_configs = []
    
    for config in configs:
        # Validate required fields
        missing_fields = [
            field for field in required_fields
            if field not in config
        ]
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
            
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
