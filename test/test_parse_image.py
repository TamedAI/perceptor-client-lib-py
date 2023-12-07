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

import os
import unittest
from perceptor_client_lib.image_parsing import convert_image_to_contextdata, _get_file_extension, _is_valid_file_type
from parameterized import parameterized

_image_path = os.path.join(os.path.dirname(__file__), "test_files", "binary_file.png")


class ImageParsingTests(unittest.TestCase):

    def test_parse_image_from_path(self):
        result = convert_image_to_contextdata(_image_path)
        self.assertEqual(result.content, f'data:image/png;base64,MXg=')

    def test_parse_image_from_buffered_reader(self):
        buffered_reader = open(_image_path, 'rb')
        with buffered_reader:
            result = convert_image_to_contextdata(buffered_reader, file_type='jpg')
        self.assertEqual(result.content, f'data:image/jpg;base64,MXg=')

    @parameterized.expand([
        None,
        ""
    ])
    def test_parse_image_from_buffered_reader_WHEN_file_type_missing_THEN_throws_error(self, file_type: str):
        buffered_reader = open(_image_path, 'rb')
        with buffered_reader:
            self.assertRaises(Exception, lambda: convert_image_to_contextdata(buffered_reader, file_type=file_type))

    def test_parse_image_from_bytes(self):
        buffered_reader = open(_image_path, 'rb')
        with buffered_reader:
            content_bytes = buffered_reader.read()
            result = convert_image_to_contextdata(content_bytes, file_type='jpg')
        self.assertEqual(result.content, f'data:image/jpg;base64,MXg=')

    @parameterized.expand([
        (_image_path, "png"),
        ("file_without_extension", "")
    ])
    def test_extension_resolved_for_file_path(self, file_path: str, expected: str):
        result = _get_file_extension(file_path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ("png", True),
        ("jpg", True),
        ("jpeg", True),
        ("PNG", True),
        ("JPG", True),
        ("JPeG", True),
        ("other", False),
        ("", False),
    ])
    def test_is_valid_file_type(self, file_extension: str, expected: bool):
        self.assertEqual(_is_valid_file_type(file_extension), expected)


if __name__ == '__main__':
    unittest.main()
