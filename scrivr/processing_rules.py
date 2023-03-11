import re
import yaml
import pypandoc
import os
import warnings
from bs4 import BeautifulSoup

class ProcessingRule:
    def process(self):
        pass

class RemoveDuplicateEmptyLinesRule(ProcessingRule):
    def process(self, text):
        return "\n".join(filter(lambda x: x.strip(), text.split("\n")))

class HtmlToMarkdownRule(ProcessingRule):
    def process(self, text):
        return pypandoc.convert_text(text, 'md', format='html')

class HtmlVisibleTextRule(ProcessingRule):
    def process(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        for element in soup.find_all(['script', 'style', 'head', 'title', 'meta', 'link']):
            element.extract()
        for element in soup.find_all(lambda tag: tag.has_attr('style') and 'display:none' in tag['style']):
            element.extract()
        return soup.get_text()

class ActionableRule(ProcessingRule):
    def __init__(self, match, action):
        self.match = match
        self.action = action

    def apply_action(self, text, match):
        if self.action == "delete":
            match = re.escape(match)
            text = re.sub(match, "", text)
        elif self.action == "delete_line":
            lines = text.split("\n")
            text = "\n".join([line for line in lines if match not in line])
        return text

class MatchAndActionRule(ActionableRule):
    def __init__(self, match, action):
        self.match = match
        self.action = action

    def process(self, text):
        pattern = re.compile(self.match)
        matches = pattern.findall(text)
        for match in matches:
            text = self.apply_action(text, match)
        return text

class MatchMultipleStringsAndActionRule(ActionableRule):
    def __init__(self, action, match=[], path=None):
        super().__init__(match, action)
        self.path = path

    def process(self, text):
        if self.path:
            if not os.path.isdir(self.path):
                warnings.warn(f"WARNING: Provided path '{self.path}' is invalid.")
                return text

            # If path is provided, read all files in the directory and concatenate their text
            for root, _, files in os.walk(self.path):
                for file in files:
                    with open(os.path.join(root, file), "r") as f:
                        self.match.append(f.read())

        for match in self.match:
            match = re.escape(match)
            pattern = re.compile(match)
            matches = pattern.findall(text)
            for m in matches:
                text = self.apply_action(text, m)
        return text

class MatchStringsAction(ActionableRule):
    def __init__(self, action, match_strings=[], path=None):
        super().__init__(match_strings, action)
        self.path = path

    def process(self, text):
        if self.path:
            if not os.path.isfile(self.path):
                warnings.warn(f"WARNING: Provided path '{self.path}' is invalid.")
                return text
            with open(self.path, "r") as f:
                file_strings = f.read().splitlines()
                self.match.extend(file_strings)

        for match in self.match:
            match = re.escape(match)
            matches = re.findall(match.strip('\n'), text)
            for m in matches:
                text = self.apply_action(text, m)
        return text

class DeleteTextAfterMatch(ProcessingRule):
    def __init__(self, match_string: str):
        self.match_string = match_string

    def process(self, text: str) -> str:
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if self.match_string in line:
                line = line.split(self.match_string)[0]
            new_lines.append(line)
        return "\n".join(new_lines)

class TableFromPattern(ProcessingRule):
    def process(self, text: str) -> str:

        # Loop this as many times as a convertable table is found
        while(True):
            lines = text.split("\n")

            # Find the start and end of the table
            start_idx = None
            end_idx = None
            for i, line in enumerate(lines):
                # Matches string starting with 3 or more `---`
                if re.match(r"^-*-{3,}", line.lstrip()):
                    if start_idx is None:
                        start_idx = i
                    elif end_idx is None:
                        end_idx = i
                        break

            # Convertable table counts as all lines between two `---` lines
            # If no convertable tables found, return text
            if (start_idx == None) or (end_idx == None):
                return text

            columns=0

            # Extract the row values and build the table body
            table_body = []
            for line in lines[start_idx+1:end_idx]:
                row_values = re.split(r"\s{3,}", line)
                if (len(row_values) > columns):
                    columns = len(row_values)
                output_row = "| " + " | ".join(row_values) + " |"
                table_body.append(output_row)

            table_header = "| " + " | ".join("-" * columns) + " |"
            table_delim = "| " + " | ".join(["---"] * columns) + " |"

            # Replace the unconverted lines with the constructed table
            del(lines[start_idx:end_idx+1])
            lines[start_idx:start_idx] = ["\n".join([table_header, table_delim] + table_body)]
            text = "\n".join(lines)


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
