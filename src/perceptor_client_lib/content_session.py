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
import logging
import time
from typing import Union

from perceptor_client_lib.external_models import PerceptorRequest, \
    InstructionWithResult, DocumentImageResult
from perceptor_client_lib.internal_models import InstructionContextData, PerceptorRepositoryRequest, \
    InstructionMethod, InstructionError, ClassifyEntry
from perceptor_client_lib.perceptor_repository import _PerceptorRepository
from perceptor_client_lib.task_limiter import TaskLimiter


class _ContentSession:

    def __init__(self, repository: _PerceptorRepository, context_data: InstructionContextData,
                 task_limiter: TaskLimiter,
                 thread_delay_factor: float):
        self._repository: _PerceptorRepository = repository
        self._logger = logging.getLogger(self.__class__.__name__)
        self._context_data: InstructionContextData = context_data
        self._thread_delay_factor: float = thread_delay_factor
        self._task_limiter = task_limiter

    async def process_instructions_request(self, request: PerceptorRequest,
                                           method: InstructionMethod,
                                           instructions: Union[str, list[str]],
                                           classify_entries: list[ClassifyEntry]) \
            -> Union[InstructionWithResult, list[InstructionWithResult]]:

        if len(instructions) == 0:
            return []

        pool_size = min(len(instructions), self._task_limiter.get_max_number_of_threads())

        async def send_single_instruction(instruction_index: int, instruction: str) -> InstructionWithResult:
            task_delay = self._thread_delay_factor * (instruction_index % pool_size)
            time.sleep(task_delay)

            response = self._process_instruction(request, method, instruction,
                                                 classify_entries)
            return response

        if isinstance(instructions, str):
            return await send_single_instruction(0, instructions)

        instructions_list: list = list(enumerate(instructions))

        task_list = map(lambda t: self._task_limiter.exec_task(send_single_instruction(t[0], t[1])), instructions_list)

        results = await asyncio.gather(*task_list)
        # noinspection PyTypeChecker
        return results

    def _process_instruction(self, request: PerceptorRequest, method: InstructionMethod,
                             instruction: str,
                             classify_entries: list[ClassifyEntry]) -> InstructionWithResult:
        self._logger.debug("processing instruction: %s", dict(instruction=instruction,
                                                              req=request,
                                                              classes=classify_entries))

        def create_repository_request() -> PerceptorRepositoryRequest:
            mapped_params = request.params.copy()
            mapped_params["returnScores"] = str(request.return_scores)
            return PerceptorRepositoryRequest(
                params=mapped_params,
                flavor=request.flavor,
                context_data=self._context_data,
                method=method
            )

        req: PerceptorRepositoryRequest = create_repository_request()

        try:
            result = self._repository.send_instruction(req, instruction, classify_entries)

            if isinstance(result, str):
                return InstructionWithResult.success(instruction, result)

            err_resp: InstructionError = result
            return InstructionWithResult.error(instruction, err_resp.error_text)
        except Exception as exc:
            self._logger.error(exc)
            return InstructionWithResult.error(instruction, str(exc))


def _map_classify_entries(string_list: list[str]):
    return list(map(lambda x: ClassifyEntry(x), string_list))


async def process_contents(repository: _PerceptorRepository,
                           data_context: Union[InstructionContextData, list[InstructionContextData]],
                           request: PerceptorRequest,
                           method: InstructionMethod,
                           instructions: Union[str, list[str]],
                           classify_entries: list[str],
                           task_limiter: TaskLimiter,
                           thread_delay_factor: float
                           ) -> Union[InstructionWithResult, list[InstructionWithResult], list[DocumentImageResult]]:
    if method == InstructionMethod.CLASSIFY and len(classify_entries) < 2:
        raise ValueError("number of classes must be > 1")

    if isinstance(data_context, InstructionContextData):
        session = _ContentSession(repository, data_context, task_limiter, thread_delay_factor)
        return await session.process_instructions_request(request, method, instructions,
                                                          _map_classify_entries(classify_entries))

    if not isinstance(data_context, list):
        raise Exception('data_context must be either InstructionContextData or list[InstructionContextData]')

    if len(data_context) == 0:
        return []

    multiple_contexts: list[InstructionContextData] = data_context

    async def process_data_context(context_info: (int, InstructionContextData)):
        page_index, ctx = context_info
        context_data: InstructionContextData = ctx
        single_session = _ContentSession(repository, context_data, task_limiter, thread_delay_factor)

        request_instruction_result = await single_session.process_instructions_request(
            request, method, instructions,
            _map_classify_entries(classify_entries))

        return DocumentImageResult(page_number=page_index,
                                   instruction_results=request_instruction_result)

    task_list = map(lambda t: process_data_context(t),
                    enumerate(multiple_contexts))

    result = await asyncio.gather(*task_list)
    # noinspection PyTypeChecker
    return result
