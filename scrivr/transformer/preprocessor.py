import os
import time
import multiprocessing
import pandas as pd
import warnings

class TransformerPreprocessor:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.df = pd.DataFrame(columns=['ingest_file_path', 'ingest_file_last_modified', 'data'])
        self.queue = multiprocessing.Queue()

        self.initialize_queue()

    def initialize_queue(self):
        # Initialize the dataframe with existing files in the directory
        rows = []
        for filename in os.listdir(self.input_dir):
            filepath = os.path.join(self.input_dir, filename)
            if os.path.isfile(filepath):
                last_modified = os.path.getmtime(filepath)
                rows.append({'ingest_file_path': filename,
                            'ingest_file_last_modified': last_modified,
                            'data': self.process_file(filename)})
        self.df = pd.concat([self.df, pd.DataFrame(rows)], ignore_index=True)

    def start(self):
        # Start watching the directory for changes
        watcher = multiprocessing.Process(target=self.watch_directory)
        watcher.start()

        # Start processing the queue of changes
        processor = multiprocessing.Process(target=self.process_queue)
        processor.start()

        # Wait for both processes to finish
        watcher.join()
        processor.join()

    def watch_directory(self):
        while True:
            # Check for new or modified files in the directory
            for filename in os.listdir(self.input_dir):
                filepath = os.path.join(self.input_dir, filename)
                if os.path.isfile(filepath):
                    last_modified = os.path.getmtime(filepath)

                    # Add the update to the queue
                    self.queue.put((filename, last_modified))

            # Wait for a short period of time before checking again
            time.sleep(1)

    def process_queue(self):
        while True:
            # Wait for an update to the DataFrame to be added to the queue
            update = self.queue.get()

            # Check if the update is a tuple with two elements
            if not isinstance(update, tuple) or len(update) != 2:
                break

            # Check if the file already exists in the DataFrame
            index = self.df.index[self.df['ingest_file_path'] == update[0]].tolist()

            if len(index) > 0:
                # Update the existing row
                self.df.at[index[0], 'ingest_file_last_modified'] = update[1]
                self.df.at[index[0], 'data'] = self.process_file(update[0])
            else:
                # Add a new row to the DataFrame
                new_row = pd.DataFrame({'ingest_file_path': [update[0]],
                                        'ingest_file_last_modified': [update[1]],
                                        'data': [self.process_file(update[0])]},
                                        )
                self.df = pd.concat([self.df, new_row], ignore_index=True)

    def process_file(self, filename):
        file_path = os.path.join(self.input_dir, filename)
        if not os.path.isfile(file_path):
            warnings.warn(f"File not found: {file_path}")
            return ''
        with open(file_path, 'r') as f:
            content = f.read()
        return content
