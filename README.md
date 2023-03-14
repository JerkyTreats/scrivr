![scrivr_long](https://user-images.githubusercontent.com/926943/222812633-909f5e22-9025-441c-880b-267603ecc9cb.png)

# SCRIVR Text Transformer

Dope ass AI shenanigan's representing an exploration into various aspects of AIDD - AI Driven Development.


> NOTE: This was fully developed using ChatGPT through prompt engineering.
>
> Some human massaging has been included, but the vast majority is pure AI created, including unit tests and the logo for this project.

## About

The intent of Scrivr is to download, process, and build fine tuned AI LLMs.

| Module      | Status |
|-------------|------------ |
| Crawler     | Not Started |
| Parser      | DONE |
| Transformer     | In Progress |

### Crawler

The intent of the crawler is to:

* Crawl html sites and download to local dir
* Have specific support for GitHub to pull relevant repos useful for fine tuning.
  * Search and clone, using the GitHub API, various repos based on a variety of factors.
  * Factors such as stars, license, tags/labels, language, etc.

### Parser

The intent of the parser is to:

* Convert text files in a given directory based on various rules
  * Currently mainly used for converting HTML to Markdown, with supporting rules to clean up the document.
* Uses multiprocessing to convert relatively large directories worth of files
* Supports a relatively complex configuration YAML to provide flexible, dynamic processing rules.

### Transformer

The intent of the transformer is to:

* Watch a directory for new/changed files
* Process those files and add to a transformer object
* Transformer tokenizes the input text
* Fine tune an LLM using the tokenized text

## History

This entire thing started by testing the coding functionality of `chat.openai.com`

I tested the ability of it to program by providing the following prompt:

```
Write me the following python script with the following specifications:

1. Take a path containing a directory of html files as a script parameter
2. Walk all files and subdirectories in the given path and parse all found html scripts
3. Parse each html file found to extract only visible text. You may use external html parsers like BeautifulSoup if you want.
4. Output each files visible text to a new .txt file
  4a. Script should require a parameter for output file path
  4b. The new file should be created in the same relative subdirectory in the output path provided. For instance, if the html file parsed was found in "docs/foo/a.html", and the output path is "/bar", the outputted file should be created in "/bar/docs/foo/a.html"
```

It gave me this:

```python
import argparse
import os
from bs4 import BeautifulSoup

# Parse command line arguments
parser = argparse.ArgumentParser(description='Extract visible text from HTML files')
parser.add_argument('input_path', metavar='input_path', type=str,
                    help='the path to the directory of HTML files')
parser.add_argument('output_path', metavar='output_path', type=str,
                    help='the path to the output directory')
args = parser.parse_args()

# Walk the directory tree
for root, dirs, files in os.walk(args.input_path):
    for file in files:
        # Check if file is HTML
        if file.endswith('.html') or file.endswith('.htm'):
            input_file_path = os.path.join(root, file)

            # Parse HTML file to extract visible text
            with open(input_file_path, 'r') as input_file:
                soup = BeautifulSoup(input_file, 'html.parser')
                visible_text = soup.get_text()

            # Determine output file path
            output_file_path = os.path.join(args.output_path, input_file_path[len(args.input_path)+1:])

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Write visible text to output file
            with open(output_file_path + '.txt', 'w') as output_file:
                output_file.write(visible_text)

```

### Working with ChatGPT

That script works, and is relatively simple. The _Holy Shit_ moment was when I started changing the specification and adding new features. ChatGPT was able to understand the context and provide a reasonable set of changes to the code based on the new requirements.

The key word here is "reasonable"- Hallucinations happen and you can't trust the code its writing.

Thankfully we've developed a trick for determining if code is trustworthy or not- unit tests.

Unit testing is absolutely necessary with ChatGPT, but thankfully is actually quite enjoyable. The worst part of unit tests is setting all the garbage up, mocking things, etc. Huge time sink, half the time I'm struggling because there's a problem with the test, not the code.

ChatGPT spits out all that setup in seconds. I just have to verify that it is actually testing what I want it to. And as unit tests are contextually contained, ChatGPT really shines in creating them.

### ChatGPT failings

What the AI Language model is _not_ good at is systems thinking. The more "contextually contained" something is the better. Complex software is a collection of black boxes taking data in and pushing data out. The AI does not do a very good job at holding the context of all those black boxes and its relation to each other.

I actually think of ChatGPT like a junior software developer, one that is frightening fast at converting English into Python. My expectations for juniors is to stuggle at the systems level, to miss edge cases and the consequences of decisions.

As a result, the program that Scrivr has become is very much the system the human has designed. Any logical flaws or missed edge cases are _my_ gaps.

## This Changes Everything

If you're a software engineer of any level, try your next toy project using AI assistance. The results are pretty frightening, because:

* These systems are unrefined, still quite janky for software development workflows.
* Even with this jank, AI assistance _markedly_ speeds up the pace of development.

It's frightening because it very much _feels_ like the nature of software development is going to fundamentally change in the next few years.

As a trivial example, leetcode in interviews is essentially obsolete. The toy challenges are something that an AI system will be able to chew through with ease. I've always been sus of the signal leetcode gives you on a software developers ability to make changes to complex systems. With AI workflows, leetcode will just give you noise.

The focus of software development will shift towards systems architecture, requirements gathering and bridging the human-software interface. Else be someone who works on a super niche area of development. But my assumption is that models will be fine-tuned to eat your lunch.

I don't think we're all going to be replaced, but I do think that the definition of what an effective software developer is about to fundamentally change.

At the very least, it will help create toy projects like this one.
