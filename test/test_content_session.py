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

import asyncio
import unittest
from typing import Union

# noinspection PyProtectedMember
from perceptor_client_lib.content_session import _ContentSession, process_contents
from perceptor_client_lib.external_models import PerceptorRequest, \
    DocumentImageResult, InstructionWithResult
# noinspection PyProtectedMember
from perceptor_client_lib.internal_models import PerceptorRepositoryRequest, TextContextData, InstructionContextData, \
    ImageContextData, InstructionMethod, _InstructionResult, InstructionError, ClassifyEntry
# noinspection PyProtectedMember
from perceptor_client_lib.perceptor_repository import _PerceptorRepository


class RepositoryMock(_PerceptorRepository):
    def __init__(self, error_response: str = None):
        self._error_response = error_response

    def send_instruction(self, request: PerceptorRepositoryRequest, instruction: str,
                         classify_entries: list[ClassifyEntry]) -> _InstructionResult:
        if self._error_response is None:
            return f"{instruction}  :: ok"
        return InstructionError(error_text=self._error_response)


_mock_repository = RepositoryMock()


class ContentSessionTests(unittest.IsolatedAsyncioTestCase):

    @staticmethod
    def _create_default_request() -> PerceptorRequest:
        return PerceptorRequest(flavor="flavour", params={})

    def test_all_instructions_are_processed(self):
        content_session = _ContentSession(_mock_repository,
                                          TextContextData("some_text"),
                                          thread_delay_factor=0)

        instructions = [
            "1",
            "2",
            "3"
        ]
        result = content_session.process_instructions_request(request=self._create_default_request(),
                                                              method=InstructionMethod.QUESTION,
                                                              instructions=instructions,
                                                              classify_entries=[],
                                                              max_number_of_threads=4)

        self.assertEqual(len(result), len(instructions))

        def get_original_instruction(t: InstructionWithResult) -> str:
            return t.instruction

        self.assertListEqual(list(map(get_original_instruction, result)),
                             instructions
                             )

    async def test_all_contents_are_processed_with_all_instructions(self):
        data_contexts: list[InstructionContextData] = [
            ImageContextData(data_uri="some_uri_1"),
            ImageContextData(data_uri="some_uri_2"),
            ImageContextData(data_uri="some_uri_3"),
        ]
        instructions: list[str] = [
            "1",
            "2",
            "3"
        ]

        result = await process_contents(_mock_repository,
                                        data_contexts,
                                        self._create_default_request(),
                                        InstructionMethod.QUESTION,
                                        instructions,
                                        classify_entries=[],
                                        max_number_of_threads=4,
                                        thread_delay_factor=0
                                        )

        self.assertEqual(len(result), len(data_contexts))
        for r in result:
            rep: Union[InstructionWithResult, list[InstructionWithResult], list[DocumentImageResult]] = r
            self.assertEqual(len(rep.instruction_results), len(instructions))

    def test_WHEN_repository_returns_error_THEN_error_in_response(self):
        repository = RepositoryMock(error_response='some error')
        content_session = _ContentSession(repository,
                                          TextContextData("some_text"),
                                          thread_delay_factor=0)
        instructions = [
            "1",
            "2",
            "3"
        ]
        result = content_session.process_instructions_request(request=self._create_default_request(),
                                                              method=InstructionMethod.QUESTION,
                                                              instructions=instructions,
                                                              classify_entries=[],
                                                              max_number_of_threads=4)

        self.assertEqual(len(result), len(instructions))
        for item in result:
            self.assertFalse(item.is_success)

    def test_WHEN_method_classify_and_number_classes_less_than_2_THEN_exception_is_raised(self):
        data_contexts = [ImageContextData(data_uri="some_uri_1")]
        instructions = ["1"]

        def _call_method():
            asyncio.run(process_contents(_mock_repository,
                                         data_contexts,
                                         self._create_default_request(),
                                         InstructionMethod.CLASSIFY,
                                         instructions,
                                         classify_entries=["x"],
                                         max_number_of_threads=1,
                                         thread_delay_factor=0
                                         ))

        self.assertRaises(ValueError, _call_method)


if __name__ == '__main__':
    unittest.main()
