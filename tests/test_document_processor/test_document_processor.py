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
        output = self.document_processor.parse_file(test_file_path, [self.rule])
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
        self.document_processor.process_files([file1_path, file2_path], [self.rule], output_dir)

        # Verify output files
        output_file1_path = os.path.join(output_dir, "file1.html")
        with open(output_file1_path, "r") as f:
            output_file1 = f.read()
        self.assertEqual(output_file1, expected_output)

        output_file2_path = os.path.join(output_dir, "file2.html")
        with open(output_file2_path, "r") as f:
            output_file2 = f.read()
        self.assertEqual(output_file2, expected_output2)



if __name__ == "__main__":
    unittest.main()
