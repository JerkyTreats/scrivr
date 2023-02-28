import os
import argparse
import multiprocessing
import yaml
from typing import List
from html_parser.processing_rules import ProcessingRule, RemoveDuplicateEmptyLinesRule



def parse_file(file_path: str, processing_rules: List[ProcessingRule]) -> str:
    """Parses a file using the provided processing rules"""
    with open(file_path, "r") as f:
        html = f.read()

    for rule in processing_rules:
        html = rule.apply(html)

    return html


def process_files(file_paths: List[str], processing_rules: List[ProcessingRule], output_dir: str) -> None:
    """Processes files using the provided processing rules and saves the results to the output directory"""
    for file_path in file_paths:
        output_file_path = os.path.join(output_dir, os.path.basename(file_path))

        html = parse_file(file_path, processing_rules)

        with open(output_file_path, "w") as f:
            f.write(html)


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


def main(input_dir: str, output_dir: str, num_processes: int, config_path: str = None) -> None:
    """Main function that processes files and writes the results to the output directory"""

    if config_path:
        processing_rules = read_config_file(config_path)
    else:
        processing_rules = [ProcessingRule.DuplicateEmptyLinesRule()]

    file_paths = [os.path.join(input_dir, file) for file in os.listdir(input_dir)]
    chunks = [[] for _ in range(num_processes)]

    for i, file_path in enumerate(file_paths):
        chunks[i % num_processes].append(file_path)

    processes = []

    for i in range(num_processes):
        p = multiprocessing.Process(
            target=process_files, args=(chunks[i], processing_rules, output_dir)
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some HTML files.")
    parser.add_argument("input_dir", help="the directory containing the HTML files to process")
    parser.add_argument("output_dir", help="the directory to write the processed HTML files to")
    parser.add_argument(
        "-n", "--num_processes", type=int, default=1, help="the number of processes to use for processing files"
    )
    parser.add_argument(
        "-c", "--config_path", help="the path to the config file to use for processing rules"
    )
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.num_processes, args.config_path)
