![scrivr_long](https://user-images.githubusercontent.com/926943/222812633-909f5e22-9025-441c-880b-267603ecc9cb.png)

# SCRIVR Text Transformer

Transforms text files with various rules.

> NOTE: This was fully developed using ChatGPT through prompt engineering.
>
> Some human massaging has been included, but the vast majority is pure AI created, including unit tests and the logo for this project.

## About

The intent of Scrivr is to download, process, and build fine tuned AI LLMs.

| Module      | Description                                                                                                                                                         | Status      |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| crawler     | * Crawl html sites and download to local dir * Support for html site and specific support for Github                                                                | Not Started |
| parser      | * Parse local html files and apply various rules * Rules allow for converting complex html files like Unity3D documentation into readable/noiseless Markdown format | DONE        |
| transformer | * Process files and transform text into LLM readable format * Use the transformed text to build a fine tuned AI language model                                      | In Progress |

