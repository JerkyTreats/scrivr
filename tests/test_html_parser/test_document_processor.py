import os
import shutil
import tempfile
import unittest
from typing import List
from document_processor.processing_rules import ProcessingRule, RemoveDuplicateEmptyLinesRule
from document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.document_processor = DocumentProcessor()
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
        self.document_processor.process_files([file1_path, file2_path], output_dir)

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
                dp.main()

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
        processing_rules:
          - type: RemoveDuplicateEmptyLinesRule
        """

        # Create test config file
        test_config_file_path = os.path.join(self.test_dir, "test_config.yaml")
        with open(test_config_file_path, "w") as f:
            f.write(test_config)

        # Load test config
        self.document_processor.config_path = test_config_file_path
        self.document_processor.main()
        self.assertEqual(self.document_processor.input_dir, "test_input")
        self.assertEqual(self.document_processor.output_dir, "test_output")
        self.assertEqual(len(self.document_processor.processing_rules), 1)
        self.assertEqual(str(self.document_processor.processing_rules[0]), "RemoveDuplicateEmptyLinesRule()")




if __name__ == "__main__":
    unittest.main()
