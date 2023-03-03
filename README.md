![scrivr_long](https://user-images.githubusercontent.com/926943/222812633-909f5e22-9025-441c-880b-267603ecc9cb.png)

# SCRIVR Text Transformer

Transforms text files with various rules.

> NOTE: This was fully developed using ChatGPT through prompt engineering.
>
> Some human massaging has been included, but the vast majority is pure AI created, including unit tests and the logo for this project.

## Installation

TBD

## Usage

Assuming the following directory structure:

```
root/
├── input/
│ ├── document1.html
│ └── document2.html
└── output/
```

And the following config file `config.yaml`:

```yaml
input_dir: '/Path/to/input'
output_dir: '/Path/to/output'
num_processes: 4
processing_rules:
  - type: HtmlVisibleText
  - type: HtmlToMarkdown
  - type: RemoveDuplicateEmptyLines
  - type: MatchMultipleStringsAndAction
    action: delete_line
    path: /Path/to/config/delete_line_string
```    

We can run scrivr with the following command:

```bash
python -m scrivr -c config.yaml
```

This will process all HTML files in the input/ directory using 4 processes, apply the specified processing rules to each file, and output the resulting files in the output/ directory.

## Processing Rules

Processing rules will take a text block, transform the text, and return the result based on the rule. 

Rules include:

1. **RemoveDuplicateEmptyLinesRule**: Removes duplicate empty lines from text.
2. **HtmlToMarkdownRule**: Converts HTML to Markdown using the pypandoc package.
3. **HtmlVisibleTextRule**: Extracts visible text from HTML using the BeautifulSoup package.
4. **ActionableRule**: An abstract class that defines an action to be performed on a text match.
5. **MatchAndActionRule**: Applies an action to all occurrences of a regex pattern in text.
6. **MatchMultipleStringsAndActionRule**: Applies an action to all occurrences of multiple strings or file contents in text.
7. **MatchStringsAction**: Applies an action to all occurrences of multiple strings in text.
