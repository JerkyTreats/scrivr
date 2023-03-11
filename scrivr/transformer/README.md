# TransformerPreprocessor

`TransformerPreprocessor` is a Python class that watches a directory for changes and processes files in that directory, storing their content in a Pandas DataFrame. It uses the watch_directory and process_queue methods to achieve this.
Usage

To use `TransformerPreprocessor`, create an instance of the class with the directory path to watch:

```python
tp = TransformerPreprocessor(/path/to/directory)
```

Then call the start method to begin watching the directory and processing files:

```python
tp.start()
```

## Initialization

When TransformerPreprocessor is initialized, it creates an empty DataFrame with columns `ingest_file_path`, `ingest_file_last_modified`, and `data`. It then scans the directory specified during initialization and adds the files in that directory to the DataFrame.

## Watching the directory for changes

The `watch_directory()` method runs in an infinite loop, checking for changes to the directory specified during initialization. If a file is added or modified in the directory, it adds an update to a queue, containing the filename and last modified time.

## Processing the queue

The process_queue method runs in an infinite loop, processing updates from the queue created by watch_directory. If a file update contains a filename and last modified time, it checks if the file already exists in the DataFrame. If it does, it updates the corresponding row with the new last modified time and file content. If it does not, it appends a new row to the DataFrame with the filename, last modified time, and file content.
Processing file content

The process_file method is used to read the content of a file in the watched directory. It takes a filename as input and returns the content of the file. It is used by process_queue to store file content in the DataFrame.

## Dependencies

`TransformerPreprocessor` requires the following dependencies:

* Python 3.x
* Pandas
* Multiprocessing
