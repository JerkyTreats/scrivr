import unittest
import os
import time
from scrivr.transformer import TransformerPreprocessor
import multiprocessing
import pandas as pd

class TestTransformerPreprocessor(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_files'
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # create some test files
        for i in range(3):
            with open(os.path.join(self.test_dir, f"test_{i}.txt"), 'w') as f:
                f.write(f"test content {i}")

    def tearDown(self):
        # remove the test files
        for filename in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, filename))
        os.rmdir(self.test_dir)

    def test_initialize_queue(self):
        # initialize the transformer preprocessor
        tp = TransformerPreprocessor(self.test_dir)

        # check that the dataframe is correctly initialized
        self.assertEqual(len(tp.df), 3)
        self.assertCountEqual(list(tp.df['ingest_file_path']), ['test_0.txt', 'test_1.txt', 'test_2.txt'])

    def test_watch_directory(self):
        # initialize the transformer preprocessor
        tp = TransformerPreprocessor(self.test_dir)

        # start watching the directory
        watcher = multiprocessing.Process(target=tp.watch_directory)
        watcher.start()

        # add a new file to the directory
        new_file = 'test_3.txt'
        with open(os.path.join(self.test_dir, new_file), 'w') as f:
            f.write("test content 3")

        # wait for two updates
        time.sleep(4)

        # check that the new file was added to the queue
        update1 = tp.queue.get()
        update2 = tp.queue.get()
        updates = [update1, update2]
        updates.sort()
        self.assertEqual(updates[0][0], 'test_2.txt')
        self.assertEqual(updates[1][0], 'test_3.txt')

        # stop the watcher
        watcher.terminate()
        watcher.join()

    def test_process_queue(self):
        # create a test DataFrame
        self.df = pd.DataFrame({
            'ingest_file_path': ['test_0.txt', 'test_1.txt'],
            'ingest_file_last_modified': [time.time(), time.time()],
            'data': ['test content 0', 'test content 1']
        })

        tp = TransformerPreprocessor(self.test_dir)

        # add a new file to the queue
        tp.queue.put(('test_2.txt', time.time()))

        # add sentinel value to signal end of queue
        tp.queue.put(None)

        # process the queue
        tp.process_queue()

        # check that the new file was added to the DataFrame
        self.assertEqual(len(tp.df), 3)
        self.assertCountEqual(list(tp.df['ingest_file_path']), ['test_0.txt', 'test_1.txt', 'test_2.txt'])

        # check that the data for the new file was processed correctly
        self.assertEqual(tp.df.loc[tp.df['ingest_file_path'] == 'test_2.txt', 'data'].values[0], 'test content 2')


if __name__ == '__main__':
    unittest.main()
