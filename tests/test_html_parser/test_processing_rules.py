import unittest
import os.path
from html_parser import read_config_file
from html_parser.processing_rules import ProcessingRule, RemoveDuplicateEmptyLinesRule

class TestConfigFile(unittest.TestCase):

    def test_no_config_file(self):
        config_file = "does_not_exist.yaml"
        with self.assertRaises(FileNotFoundError):
            read_config_file(config_file)

    def test_invalid_processing_rule(self):
        config_file = "invalid_config.yaml"
        with open(config_file, 'w') as f:
            f.write("processing_rules:\n  - InvalidProcessingRule\n")
        with self.assertRaises(ValueError):
            read_config_file(config_file)
        os.remove(config_file)

    def test_nonexistent_config_file(self):
        config_file = "nonexistent_config.yaml"
        with self.assertRaises(FileNotFoundError):
            read_config_file(config_file)

    def test_valid_config_file(self):
        config_file = "valid_config.yaml"
        with open(config_file, 'w') as f:
            f.write("processing_rules:\n  - type: RemoveDuplicateEmptyLinesRule\n")
        result = read_config_file(config_file)
        expected_rule = RemoveDuplicateEmptyLinesRule()
        assert len(result) == 1
        assert type(result[0]) == type(expected_rule)
        os.remove(config_file)

class TestRemoveDuplicateEmptyLinesRule(unittest.TestCase):

    def test_process(self):
        rule = RemoveDuplicateEmptyLinesRule()
        input_text = "This is a test\n\n\nof the empty line removal rule.\n\n\n\n\nIt should remove all duplicate empty lines."
        expected_output = "This is a test\nof the empty line removal rule.\nIt should remove all duplicate empty lines."
        output_text = rule.process(input_text)
        self.assertEqual(output_text, expected_output)

if __name__ == '__main__':
    unittest.main()
