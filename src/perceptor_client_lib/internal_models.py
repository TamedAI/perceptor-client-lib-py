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

from enum import Enum
from typing import Union
from dataclasses import dataclass

from pydantic import BaseModel


class InstructionMethod(Enum):
    QUESTION = 1
    TABLE = 2
    CLASSIFY = 3


class InstructionContextData(BaseModel):
    context_type: str
    content: str


class ImageContextData(InstructionContextData):
    def __init__(self, data_uri: str):
        super().__init__(context_type="image", content=data_uri)


class TextContextData(InstructionContextData):
    def __init__(self, text_to_process: str):
        super().__init__(context_type="text", content=text_to_process)


@dataclass
class ClassifyEntry:
    value: str


class PerceptorRepositoryRequest(BaseModel):
    flavor: str
    params: dict
    context_data: InstructionContextData
    method: InstructionMethod = InstructionMethod.QUESTION


class InstructionError(BaseModel):
    """
    Information on error occurred during instruction's processing.
    """
    error_text: str
    """
    True if the error is worth retrying
    """
    is_retryable: bool = True


_InstructionResult = Union[str, InstructionError]
