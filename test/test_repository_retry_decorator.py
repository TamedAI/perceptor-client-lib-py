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

from perceptor_client_lib.internal_models import PerceptorRepositoryRequest, InstructionContextData, \
    InstructionMethod, _InstructionResult, InstructionError, ClassifyEntry
from perceptor_client_lib.perceptor_repository import _PerceptorRepository
from perceptor_client_lib.perceptor_repository_retrydecorator import _PerceptorRepositoryRetryDecorator


class RepositoryMock(_PerceptorRepository):
    def __init__(self, to_return: _InstructionResult):
        self._to_return = to_return

    def send_instruction(self, request: PerceptorRepositoryRequest, instruction: str,
                         classify_entries: list[ClassifyEntry]) -> _InstructionResult:
        return self._to_return


request_to_send = PerceptorRepositoryRequest(
    flavor="some_flavor",
    params={},
    context_data=InstructionContextData(context_type="text", content="some content"),
    method=InstructionMethod.QUESTION
)


class PerceptorRepositoryRetryDecoratorTests(unittest.TestCase):

    @staticmethod
    def _create_decorated_repository(to_return: _InstructionResult):
        return _PerceptorRepositoryRetryDecorator(RepositoryMock(to_return))

    def test_retryable_error_rethrown(self):
        repository_error = InstructionError(error_text="some error", is_retryable=True)
        mock_repository = self._create_decorated_repository(repository_error)
        result = mock_repository.send_instruction(request_to_send, "some_instruction", [])

        self.assertIs(result, repository_error)

    def test_unrecoverable_error_rethrown(self):
        repository_error = InstructionError(error_text="some error", is_retryable=False)
        mock_repository = self._create_decorated_repository(repository_error)
        result = mock_repository.send_instruction(request_to_send, "some_instruction", [])

        self.assertIs(result, repository_error)


if __name__ == '__main__':
    unittest.main()
