import os
import io
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from typing import List
from document_processor.processing_rules import RemoveDuplicateEmptyLinesRule,HtmlToMarkdownRule
from document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.document_processor = DocumentProcessor()
        self.output_dir = os.path.join(self.test_dir, 'output')
        self.rule = RemoveDuplicateEmptyLinesRule()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_parse_file(self) -> None:
        # Create test file
        test_file_path = os.path.join(self.test_dir, "test.html")
        with open(test_file_path, "w") as f:
            f.write("<html>\n<head>\n<title>Test</title>\n</head>\n<body>\n<p>Test paragraph.</p>\n\n</body>\n</html>")

        # Parse test file
        expected_output = "<html>\n<head>\n<title>Test</title>\n</head>\n<body>\n<p>Test paragraph.</p>\n</body>\n</html>"
        self.document_processor.processing_rules = [self.rule]
        output = self.document_processor.parse_file(test_file_path)
        self.assertEqual(output, expected_output)

    def test_process_files(self) -> None:
        # Create test files
        file1_path = os.path.join(self.test_dir, "file1.html")
        with open(file1_path, "w") as f:
            f.write("<html>\n<head>\n<title>File 1</title>\n</head>\n<body>\n<p>Test paragraph.</p>\n\n</body>\n</html>")
        file2_path = os.path.join(self.test_dir, "file2.html")
        with open(file2_path, "w") as f:
            f.write("<html>\n<head>\n<title>File 2</title>\n</head>\n<body>\n<p>Test paragraph.</p>\n\n</body>\n</html>")

        # Process test files
        expected_output = "<html>\n<head>\n<title>File 1</title>\n</head>\n<body>\n<p>Test paragraph.</p>\n</body>\n</html>"
        expected_output2 = "<html>\n<head>\n<title>File 2</title>\n</head>\n<body>\n<p>Test paragraph.</p>\n</body>\n</html>"
        output_dir = os.path.join(self.test_dir, "output")
        os.mkdir(output_dir)

        self.document_processor.processing_rules = [self.rule]
        self.document_processor.input_dir = self.test_dir
        self.document_processor.output_dir = output_dir
        self.document_processor.num_processes = 1
        self.document_processor.process_files()

        # Verify output files
        output_file1_path = os.path.join(output_dir, "file1.html")
        with open(output_file1_path, "r") as f:
            output_file1 = f.read()
        self.assertEqual(output_file1, expected_output)

        output_file2_path = os.path.join(output_dir, "file2.html")
        with open(output_file2_path, "r") as f:
            output_file2 = f.read()
        self.assertEqual(output_file2, expected_output2)

    def test_subdirectory_files_read(self):
            # Create a temporary directory with some subdirectories and files
            with tempfile.TemporaryDirectory() as tempdir:
                subdirs = ['subdir1', 'subdir2']
                files = ['file1.html', 'file2.html', 'file3.html']
                for subdir in subdirs:
                    subdir_path = os.path.join(tempdir, subdir)
                    os.makedirs(subdir_path)
                    for file in files:
                        with open(os.path.join(subdir_path, file), 'w') as f:
                            f.write('<html><head><title>{}</title></head><body></body></html>'.format(file))

                # Run the DocumentProcessor on the temporary directory
                dp = DocumentProcessor(input_dir=tempdir, output_dir=tempdir)
                dp.process_files()

                # Check that all the files were processed
                for subdir in subdirs:
                    subdir_path = os.path.join(tempdir, subdir)
                    for file in files:
                        processed_path = os.path.join(tempdir, os.path.relpath(os.path.join(subdir_path, file), tempdir))
                        self.assertTrue(os.path.exists(processed_path))
                        with open(processed_path, 'r') as f:
                            processed_html = f.read()
                            self.assertIn('<title>{}</title>'.format(file), processed_html)

    def test_load_config(self) -> None:
        # Create test config
        test_config = """
        input_dir: test_input
        output_dir: test_output
        num_processes: 2
        processing_rules:
          - type: RemoveDuplicateEmptyLinesRule
        """

        # Create test config file
        test_config_file_path = os.path.join(self.test_dir, "test_config.yaml")
        with open(test_config_file_path, "w") as f:
            f.write(test_config)

        # Load test config
        self.document_processor.config_path = test_config_file_path
        self.document_processor.load_config()
        self.assertEqual(self.document_processor.input_dir, "test_input")
        self.assertEqual(self.document_processor.output_dir, "test_output")
        self.assertEqual(self.document_processor.num_processes, 2)
        self.assertEqual(len(self.document_processor.processing_rules), 1)
        assert isinstance(self.document_processor.processing_rules[0], RemoveDuplicateEmptyLinesRule)

    def test_main_no_input_directory(self):
        processor = DocumentProcessor()
        with self.assertRaises(ValueError) as cm:
            processor.process_files()
        self.assertEqual(str(cm.exception), "No input directory specified.")

    def test_main_no_output_directory(self):
        processor = DocumentProcessor(input_dir='test_input')
        with self.assertRaises(ValueError) as cm:
            processor.process_files()
        self.assertEqual(str(cm.exception), "No output directory specified.")

    def test_output_dir_created(self):
        input_dir = os.path.join(os.path.dirname(__file__), 'test_files', 'input_dir')
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'output_dir')
            self.document_processor.input_dir = input_dir
            self.document_processor.output_dir = output_dir
            self.document_processor.process_files()
            self.assertTrue(os.path.exists(output_dir))

    @patch("multiprocessing.Process")
    def test_main_multiprocessing(self, mock_process):
        input_dir = os.path.join(os.path.dirname(__file__), "test_files")
        output_dir = os.path.join(self.test_dir, "output")

        document_processor = DocumentProcessor(input_dir=input_dir, output_dir=output_dir, num_processes=2)
        document_processor.process_files()

        mock_process.assert_called_with(
            target=document_processor.process_files_chunk,
            args=([],),
        )


class TestParseFile(unittest.TestCase):
    def setUp(self) -> None:
        self.document_processor = DocumentProcessor()

    def test_parse_file_html(self):
        html_text = '<html><body><h1>Hello, world!</h1><p>This is some text.</p></body></html>'
        expected_output = '# Hello, world!\nThis is some text.'

        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as html_file:
            html_file.write(html_text)
            html_file_path = html_file.name

        self.document_processor.processing_rules = [HtmlToMarkdownRule(), RemoveDuplicateEmptyLinesRule()]

        result = self.document_processor.parse_file(html_file_path)

        self.assertEqual(result, expected_output)

        os.remove(html_file_path)

if __name__ == "__main__":
    unittest.main()
