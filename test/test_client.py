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

from perceptor_client_lib.external_models import PerceptorRequest
# noinspection PyProtectedMember
from perceptor_client_lib.internal_models import PerceptorRepositoryRequest, _InstructionResult, ClassifyEntry
from perceptor_client_lib.perceptor import Client
# noinspection PyProtectedMember
from perceptor_client_lib.perceptor_repository import _PerceptorRepository

_image_path = os.path.join(os.path.dirname(__file__), "test_files", "binary_file.png")
_invoice_path = os.path.join(os.path.dirname(__file__), "test_files", "image_with_invoice_table.png")
_pdf_path = os.path.join(os.path.dirname(__file__), "test_files", "pdf_with_2_pages.pdf")

EXPECTED_PDF_PAGES = 2


class RepositoryMock(_PerceptorRepository):
    def send_instruction(self, request: PerceptorRepositoryRequest, instruction: str,
                         classify_entries: list[ClassifyEntry]) -> _InstructionResult:
        return f"{instruction}  :: ok"


def _create_client_with_mock_repository():
    client = Client("api_key", "api_url", max_level_of_parallelization=2)
    client._repository = RepositoryMock()
    return client


_client_with_mock_repository = _create_client_with_mock_repository()


class ClientMethodsTest(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def create_default_request():
        return PerceptorRequest.with_flavor("original")

    @staticmethod
    def _get_response_text(inp: dict) -> str:
        return inp.get("text", "")

    def assert_response_text_equals(self, first: str, second: dict):
        self.assertEqual(first, self._get_response_text(second))

    @staticmethod
    def _create_client_for(api_key: str, api_url: str):
        Client(api_key, api_url)

    def test_WHEN_creating_default_request_THEN_params_are_filled(self):
        request = PerceptorRequest.with_flavor("original")
        self.assertTrue(len(request.params.items()) > 0)

    def test_WHEN_apikey_missing_THEN_exception_is_thrown(self):
        with self.assertRaises(ValueError) as ctx:
            self._create_client_for("", "some_url")
        self.assertTrue("api_key" in str(ctx.exception))
        pass

    def test_WHEN_request_url_missing_THEN_exception_is_thrown(self):
        with self.assertRaises(ValueError) as ctx:
            self._create_client_for("some_key", "")
        self.assertTrue("request_url" in str(ctx.exception))
        pass

    async def test_ask_text(self):
        instructions = ["1", "2"]
        result = await _client_with_mock_repository.ask_text("text_to_ask", instructions=instructions,
                                                             request_parameters=self.create_default_request())
        self.assertEqual(len(result), len(instructions))

    async def test_ask_image_from_file(self):
        instructions = ["1", "2"]
        result = await _client_with_mock_repository.ask_image(_image_path, instructions=instructions,
                                                              request_parameters=self.create_default_request())
        self.assertEqual(len(result), len(instructions))

    async def test_ask_image_from_file_reader(self):
        instructions = ["1", "2"]

        reader = open(_image_path, 'rb')
        with reader:
            result = await _client_with_mock_repository.ask_image(reader, file_type="png",
                                                                  instructions=instructions,
                                                                  request_parameters=self.create_default_request())
            self.assertEqual(len(result), len(instructions))

    async def test_ask_table_from_image_file(self):
        instruction = "instruction query text"
        result = await (_client_with_mock_repository.
                        ask_table_from_image(_image_path,
                                             instruction=instruction,
                                             request_parameters=self.create_default_request()))
        self.assert_response_text_equals(f"{instruction}  :: ok", result.response)

    async def test_ask_document_from_file(self):
        instructions = ["1", "2"]
        image_results = await (_client_with_mock_repository
                               .ask_document(_pdf_path, instructions=instructions,
                                             request_parameters=self.create_default_request()))
        self.assertEqual(len(image_results), EXPECTED_PDF_PAGES)
        for single_result in image_results:
            self.assertEqual(len(single_result.instruction_results), len(instructions))

    async def test_classify_document_from_file(self):
        instruction = "some instruction"
        image_results = await _client_with_mock_repository.classify_document(_pdf_path, instruction=instruction,
                                                                             classes=["a", "b"],
                                                                             request_parameters=self.create_default_request())
        self.assertEqual(len(image_results), EXPECTED_PDF_PAGES)

    async def test_ask_document_images_from_files(self):
        file_paths = [_image_path, _invoice_path, _invoice_path]
        instructions = ["inst1", "inst no. 2"]
        image_results = await _client_with_mock_repository.ask_document_images(file_paths, instructions=instructions,
                                                                               request_parameters=self.create_default_request())
        self.assertEqual(len(image_results), len(file_paths))
        self.assertEqual(image_results[0].page_number, 0)
        self.assertEqual(image_results[1].page_number, 1)
        for single_result in image_results:
            self.assertEqual(len(single_result.instruction_results), len(instructions))

    async def test_classify_document_images_from_files(self):
        file_paths = [_image_path, _invoice_path, _invoice_path]
        instruction = "some instruction"
        image_results = (
            await _client_with_mock_repository.classify_document_images(file_paths,
                                                                        instruction=instruction,
                                                                        classes=["a", "b"],
                                                                        request_parameters=self.create_default_request()))
        self.assertEqual(len(image_results), len(file_paths))
        self.assertEqual(image_results[0].page_number, 0)
        self.assertEqual(image_results[1].page_number, 1)

    async def test_ask_table_from_document_file(self):
        instruction = "instruction query text"
        page_results = await _client_with_mock_repository.ask_table_from_document(_pdf_path,
                                                                                  instruction=instruction,
                                                                                  request_parameters=self.create_default_request())
        self.assertEqual(len(page_results), EXPECTED_PDF_PAGES)
        for r in page_results:
            single_result = r.instruction_results
            self.assertEqual(True, single_result.is_success)
            self.assert_response_text_equals(f"{instruction}  :: ok", single_result.response)

    async def test_ask_table_from_document_images_from_files(self):
        file_paths = [_image_path, _invoice_path, _invoice_path]
        instruction = "instruction query text"
        page_results = await _client_with_mock_repository.ask_table_from_document_images(file_paths,
                                                                                         instruction=instruction,
                                                                                         request_parameters=self.create_default_request())
        self.assertEqual(len(page_results), len(file_paths))
        for r in page_results:
            single_result = r.instruction_results
            self.assertEqual(True, single_result.is_success)
            self.assert_response_text_equals(f"{instruction}  :: ok", single_result.response)


if __name__ == '__main__':
    unittest.main()
