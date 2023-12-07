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

import json
from json import JSONDecodeError
from typing import Union

import requests
import sseclient
from pydantic import BaseModel
from requests import Response

from perceptor_client_lib.internal_models import PerceptorRepositoryRequest, InstructionMethod, _InstructionResult, \
    InstructionError, ClassifyEntry


class PerceptorRepositoryHttpClientSettings(BaseModel):
    api_key: str
    request_url: str
    wait_timeout: int


class _PerceptorRepository:
    def send_instruction(self, request: PerceptorRepositoryRequest,
                         instruction: str,
                         classify_entries: list[ClassifyEntry]) -> _InstructionResult:
        raise Exception("not implemented, must override")


class _PerceptorRepositoryHttpClient(_PerceptorRepository):

    def __init__(self, settings: PerceptorRepositoryHttpClientSettings):
        self._settings: PerceptorRepositoryHttpClientSettings = settings
        self._headers: dict[str, str] = {
            'Accept': 'text/event-stream',
            'Authorization': 'Bearer ' + self._settings.api_key
        }

    @staticmethod
    def _fiter_events(event: sseclient.Event) -> bool:
        return event.event == 'finished'

    def _create_body(self,
                     request: PerceptorRepositoryRequest,
                     instruction: str,
                     classes: Union[list[ClassifyEntry], None]) -> dict:
        result = {
            "flavor": request.flavor,
            "contextType": request.context_data.context_type,
            "context": request.context_data.content,
            "params": request.params,
            "waitTimeout": self._settings.wait_timeout,
            "instruction": instruction
        }

        if classes is not None:
            result["classes"] = list(map(lambda x: x.value, classes))
        return result

    def _map_successful_response(self, request_response: Response) -> str:
        with request_response:
            if len(request_response.content) == 0:
                event_list = []
            else:
                client = sseclient.SSEClient(request_response)
                client_events = client.events()
                event_list = list(filter(self._fiter_events, client_events))

        if len(event_list) > 0:
            return event_list[0].data

        return ""

    @staticmethod
    def _parse_bad_response_text(request_response: Response) -> InstructionError:
        try:
            parsed_json = json.loads(request_response.text)
            return InstructionError(error_text=parsed_json['detail'], is_retryable=False)
        except JSONDecodeError:
            return InstructionError(error_text=request_response.text, is_retryable=False)

    def send_instruction(self, request: PerceptorRepositoryRequest,
                         instruction: str,
                         classify_entries: list[ClassifyEntry]) -> _InstructionResult:
        def get_body():
            if request.method == InstructionMethod.CLASSIFY:
                return self._create_body(request, instruction, classify_entries)
            return self._create_body(request, instruction, classes=None)

        body = get_body()

        def resolve_method():
            if request.method == InstructionMethod.TABLE:
                return 'generate_table'
            if request.method == InstructionMethod.CLASSIFY:
                return 'classify'
            return 'generate'

        request_url = f"{self._settings.request_url}{resolve_method()}"

        try:
            request_response: Response = requests.post(request_url,
                                                       stream=True,
                                                       headers=self._headers,
                                                       json=body)
        except Exception as exc:
            return InstructionError(error_text=str(exc), is_retryable=True)

        with request_response:
            if request_response.status_code == 200:
                return self._map_successful_response(request_response)

            if request_response.status_code == 403:
                return InstructionError(error_text="invalid api_key", is_retryable=False)

            if request_response.status_code == 400:
                return self._parse_bad_response_text(request_response)

            if request_response.status_code == 404:
                return InstructionError(error_text="not found", is_retryable=False)

            return InstructionError(error_text=str(request_response.content), is_retryable=True)
