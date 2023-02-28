# html_parser

This was fully developed using ChatGPT through prompt engineering.

Some human massaging has been included, but the vast majority is pure AI created, including unit tests and the majority of this README.

## Installation

TBD

## Usage

Here's an example of how to use `html_parser`:

```python
from html_parser import HtmlParser, read_config_file

# Read the configuration file
config_file = "config.yaml"
processing_rules = read_config_file(config_file)

# Create a HtmlParser instance
parser = HtmlParser()

# Parse an HTML file and apply processing rules
input_file = "input.html"
output_file = "output.html"
parser.parse(input_file, output_file, processing_rules)
```

## Processing Rules

This configuration file specifies a single processing rule, which is an instance of the RemoveDuplicateEmptyLinesRule class.

html_parser includes a number of built-in processing rules, which are defined in the processing_rules module. You can also define your own custom processing rules by subclassing the ProcessingRule class and implementing a process method.

Here's an example processing rule that removes duplicate empty lines:

```python

from html_parser.processing_rules import ProcessingRule

class RemoveDuplicateEmptyLinesRule(ProcessingRule):
    def process(self, text):
        return "\n".join(filter(lambda x: x.strip(), text.split("\n")))
```

To use this processing rule, you would include the following configuration in your configuration file:

```yaml

processing_rules:
  - type: RemoveDuplicateEmptyLinesRule
```
