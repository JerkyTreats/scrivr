import yaml

class ProcessingRule:
    pass

class RemoveDuplicateEmptyLinesRule(ProcessingRule):
    def process(self, text):
        return "\n".join(filter(lambda x: x.strip(), text.split("\n")))

def create_processing_rule(rule_config):
    """
    Creates a ProcessingRule object from a configuration dictionary.

    Args:
        rule_config (dict): A dictionary containing the configuration for the ProcessingRule.

    Returns:
        ProcessingRule: A ProcessingRule object corresponding to the configuration dictionary.

    Raises:
        ValueError: If the rule_config dictionary is not valid or if the ProcessingRule type is invalid.
    """
    if not isinstance(rule_config, dict):
        raise ValueError("Invalid rule configuration")

    rule_type = rule_config.pop('type')
    rule_class = globals().get(rule_type)
    if not rule_class or not issubclass(rule_class, ProcessingRule):
        raise ValueError(f"Invalid processing rule type: {rule_type}")
    return rule_class(**rule_config)

def read_config_file(file_path):
    """
    Reads a YAML configuration file and returns a list of ProcessingRule objects
    that correspond to the rules specified in the configuration file.

    Args:
        file_path (str): The path to the YAML configuration file.

    Returns:
        List[ProcessingRule]: A list of ProcessingRule objects corresponding to the rules specified in the config file.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If there is an error parsing the YAML in the configuration file or creating a ProcessingRule object.
    """
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Config file not found at path: {file_path}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML in config file at path: {file_path}") from e

    processing_rules = []
    for rule_config in config.get('processing_rules', []):
        try:
            processing_rule = create_processing_rule(rule_config)
            processing_rules.append(processing_rule)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Error creating processing rule from config: {rule_config}") from e

    return processing_rules
