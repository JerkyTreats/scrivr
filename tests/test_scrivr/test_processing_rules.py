import unittest
import os.path
from scrivr.processing_rules import *
import shutil
import tempfile
import pytest
from bs4 import BeautifulSoup
import textwrap

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

class TestHtmlToMarkdownRule(unittest.TestCase):
    def setUp(self):
        self.rule = HtmlToMarkdownRule()

    def test_process(self):
        # Test valid HTML to markdown conversion
        html = '<h1>This is a heading</h1><p>This is a paragraph.</p>'
        expected_output = '# This is a heading\n\nThis is a paragraph.\n'
        output = self.rule.process(html)
        self.assertEqual(output, expected_output)

class TestMatchAndActionRule(unittest.TestCase):
    def test_process(self):
        input_text = "This is some text to match and delete"
        rule_config = {"type": "MatchAndActionRule", "match": "match and delete", "action": "delete"}
        rule = create_processing_rule(rule_config)
        output_text = rule.process(input_text)
        expected_output = "This is some text to "
        assert output_text == expected_output

    def test_process_replace_text_with_replacement(self):
        input_text = "The quick brown fox jumps over the lazy dog"
        expected_output = "The quick red fox jumps over the lazy dog"
        rule = MatchAndActionRule("brown", "replace_text", "red")
        output_text = rule.process(input_text)
        self.assertEqual(output_text, expected_output)

class TestMatchMultipleStringsAndActionRule(unittest.TestCase):
    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_process_remove_from_middle(self):
        html = 'test\nhello\ntest\n'
        expected_output = 'test\n\ntest\n'
        rule = MatchMultipleStringsAndActionRule('delete', ['hello'])
        output = rule.process(html)
        self.assertEqual(output, expected_output)

    def test_process(self):
        input_str = "This is a test string that contains multiple matching strings"
        rule_config = {
            "type": "MatchMultipleStringsAndActionRule",
            "match": ["test", "multiple matching"],
            "action": "delete"
        }
        rule = create_processing_rule(rule_config)
        output_str = rule.process(input_str)
        assert output_str == "This is a  string that contains  strings"

    def test_match_multiple_strings_and_action_rule_with_path(self):
        # create test files with specific content
        file1 = os.path.join(self.tmp_path, "file1.txt")
        with open(file1, "w") as f:
            f.write("This is")
        file2 = os.path.join(self.tmp_path, "file2.txt")
        with open(file2, "w") as f:
            f.write("some more")

        # create processing rule config
        rule_config = {
            "type": "MatchMultipleStringsAndActionRule",
            # "match": ["text", "more text"],
            "action": "delete",
            "path": self.tmp_path,
        }

        # create processing rule and apply it to test string
        rule = create_processing_rule(rule_config)
        text = "This is some text to match and delete. This is some more text to match and delete."
        processed_text = rule.process(text)

        # assert that expected text is removed
        expected_text = " some text to match and delete.   text to match and delete."
        assert processed_text == expected_text

        rule_config = {
            "type": "MatchMultipleStringsAndActionRule",
            "match": ["text", "more text"],
            "action": "delete",
            "path": self.tmp_path,
        }

        rule = create_processing_rule(rule_config)
        text = "This is some text to match and delete. This is some more text to match and delete."
        processed_text = rule.process(text)

        # assert that expected text is removed
        expected_text = " some  to match and delete.    to match and delete."
        assert processed_text == expected_text

    def test_match_multiple_strings_and_action_rule_with_invalid_path(self):
        rule_config = {
            "type": "MatchMultipleStringsAndActionRule",
            "match": ["test", "multiple matching"],
            "action": "delete",
            "path": "invalid_path",
        }
        rule = create_processing_rule(rule_config)
        input_str = "This is a test string that contains multiple matching strings"
        with pytest.warns(UserWarning):
            output_str = rule.process(input_str)

class TestMatchStringsAction(unittest.TestCase):
    def test_process(self):
        text = "The quick brown fox jumps over the lazy dog"
        expected_output = "The  brown  jumps over the  dog"
        rule = MatchStringsAction(match_strings=["quick", "fox", "lazy"], action="delete")
        output = rule.process(text)
        self.assertEqual(output.strip(), expected_output.strip())

    def test_match_strings_action_delete_line(self):
        text = "Hello\nWorld\nBye\n"
        expected_output = "World\n"
        rule = MatchStringsAction(action="delete_line", match_strings=["Hello", "Bye"])
        output = rule.process(text)
        self.assertEqual(output.strip(), expected_output.strip())

class TestHtmlVisibleTextRule(unittest.TestCase):
    def test_process(self):
        html = '<html><head><title>Test</title></head><body><div style="display:none">This text should be hidden.</div><p>This is the visible text.</p></body></html>'
        expected_output = '<p>This is the visible text.</p>'
        rule = HtmlVisibleTextRule()
        output = rule.process(html)
        soup_expected = BeautifulSoup(expected_output, 'html.parser')
        soup_output = BeautifulSoup(output, 'html.parser')
        self.assertEqual(soup_expected.text, soup_output.text)

class TestDeleteTextAfterMatch(unittest.TestCase):
    def test_delete_line_after_match(self):
        input_text = "This is the first line\nThis exists{#This text should be deleted\n#} Some other text on a new line"
        expected_output = "This is the first line\nThis exists\n#} Some other text on a new line"

        rule = DeleteTextAfterMatch("{#")
        output_text = rule.process(input_text)

        self.assertEqual(output_text, expected_output)

class TestTableFromPattern(unittest.TestCase):

    def test_create_table_from_pattern(self):
        input_text = textwrap.dedent("""
        This test begins like this.
        It is very good.

        ---- ---- ---- ----
        Anotr bol    Bigg wha    Colo    Dolo bing
        1    2    3    4
        5    6    7    8
        ---- ---- ---- ----

        This comes after the table.
        """)
        expected_output = textwrap.dedent("""
        This test begins like this.
        It is very good.

        | - | - | - | - |
        | --- | --- | --- | --- |
        | Anotr bol | Bigg wha | Colo | Dolo bing |
        | 1 | 2 | 3 | 4 |
        | 5 | 6 | 7 | 8 |

        This comes after the table.
        """)

        rule = TableFromPattern()
        output_text = rule.process(input_text)
        print('')
        print(output_text)
        assert output_text == expected_output

    def test_create_multiple_table_from_pattern(self):
        input_text = textwrap.dedent("""
        This test begins like this.
        It is very good.

        ---- ---- ---- ----
        Anotr bol    Bigg wha    Colo    Dolo bing
        1    2    3    4
        5    6    7    8
        ---- ---- ---- ----

        This comes after the table.

        ---- ----
        You know it   Hello
        1    2
        5    6
        ---- ----
        """)
        expected_output = textwrap.dedent("""
        This test begins like this.
        It is very good.

        | - | - | - | - |
        | --- | --- | --- | --- |
        | Anotr bol | Bigg wha | Colo | Dolo bing |
        | 1 | 2 | 3 | 4 |
        | 5 | 6 | 7 | 8 |

        This comes after the table.

        | - | - |
        | --- | --- |
        | You know it | Hello |
        | 1 | 2 |
        | 5 | 6 |
        """)

        rule = TableFromPattern()
        output_text = rule.process(input_text)
        print('')
        print(output_text)
        assert output_text == expected_output

if __name__ == '__main__':
    unittest.main()
