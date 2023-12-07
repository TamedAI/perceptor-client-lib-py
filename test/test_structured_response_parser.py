#  Copyright 2023 TamedAI GmbH
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unittest
from string import Template

from parameterized import parameterized

from perceptor_client_lib.structured_response_parser import _parse_structured_text, _KEY_NAME_TEXT


class StructuredResponseParserTests(unittest.TestCase):

    def test_json_text_parsed_to_structure(self):
        direct_answer = "direct_answer_text"
        to_parse = Template("""
        {"text": "$direct_answer", "scores": {"score": 0.6433784365653992, "n_tokens": 5}}
        """).substitute(direct_answer=direct_answer)
        result = _parse_structured_text(to_parse)
        self.assertIsNotNone(result)
        self.assertEqual(result[_KEY_NAME_TEXT], direct_answer)

    def test_json_without_text_element_returns_empty_text(self):
        to_parse = """
        {"scores": {"score": 0.6433784365653992, "n_tokens": 5}}
        """
        result = _parse_structured_text(to_parse)
        self.assertIsNotNone(result)
        self.assertEqual(result[_KEY_NAME_TEXT], "")

    @parameterized.expand([
        "direct_answer_text",
        "2"
        ""
    ])
    def test_non_json_text_parsed_to_text_element(self, direct_answer: str):
        to_parse = direct_answer
        result = _parse_structured_text(to_parse)
        self.assertIsNotNone(result)
        self.assertEqual(result[_KEY_NAME_TEXT], direct_answer)


if __name__ == '__main__':
    unittest.main()
