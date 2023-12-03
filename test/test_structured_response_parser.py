import unittest
from string import Template

from parameterized import parameterized

from perceptor_client_lib.structured_response_parser import parse_structured_text, _KEY_NAME_TEXT


class StructuredResponseParserTests(unittest.TestCase):

    def test_json_text_parsed_to_structure(self):
        direct_answer = "direct_answer_text"
        to_parse = Template("""
        {"text": "$direct_answer", "scores": {"score": 0.6433784365653992, "n_tokens": 5}}
        """).substitute(direct_answer=direct_answer)
        result = parse_structured_text(to_parse)
        self.assertIsNotNone(result)
        self.assertEqual(result[_KEY_NAME_TEXT], direct_answer)

    def test_json_without_text_element_returns_empty_text(self):
        to_parse = """
        {"scores": {"score": 0.6433784365653992, "n_tokens": 5}}
        """
        result = parse_structured_text(to_parse)
        self.assertIsNotNone(result)
        self.assertEqual(result[_KEY_NAME_TEXT], "")

    @parameterized.expand([
        "direct_answer_text",
        "2"
        ""
    ])
    def test_non_json_text_parsed_to_text_element(self, direct_answer: str):
        to_parse = direct_answer
        result = parse_structured_text(to_parse)
        self.assertIsNotNone(result)
        self.assertEqual(result[_KEY_NAME_TEXT], direct_answer)


if __name__ == '__main__':
    unittest.main()
