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

from tenacity import *
import logging
import tenacity

from perceptor_client_lib.internal_models import PerceptorRepositoryRequest, _InstructionResult, InstructionError, \
    ClassifyEntry
from perceptor_client_lib.perceptor_repository import _PerceptorRepository


class _PerceptorRepositoryRetryDecorator(_PerceptorRepository):
    def __init__(self, decoree: _PerceptorRepository, max_retries: int = 3):
        self._decoree: _PerceptorRepository = decoree
        self._number_of_retries: int = max_retries

    def log_attempt_number(self, retry_state: RetryCallState):
        logger = logging.getLogger(self.__class__.__name__)
        logger.warning("retrying (%s) request...", retry_state.attempt_number)

    def send_instruction(self, request: PerceptorRepositoryRequest, instruction: str,
                         classify_entries: list[ClassifyEntry]) -> _InstructionResult:
        def to_call():
            return self._decoree.send_instruction(request, instruction, classify_entries)

        def should_retry(r):
            if isinstance(r, InstructionError):
                err: InstructionError = r
                return err.is_retryable
            return False

        def return_last_value(retry_state):
            return retry_state.outcome.result()

        retry_wrap_fn = tenacity.retry(
            stop=stop_after_attempt(self._number_of_retries),
            reraise=True,
            retry=tenacity.retry_if_result(should_retry),
            retry_error_callback=return_last_value,
            wait=tenacity.wait_exponential(multiplier=0.02, max=1),
            before_sleep=self.log_attempt_number
        )(to_call)

        return retry_wrap_fn()
