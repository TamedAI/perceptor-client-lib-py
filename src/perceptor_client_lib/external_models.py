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

from dataclasses import dataclass, field
from typing import Union, Optional

from pydantic import BaseModel

from perceptor_client_lib.structured_response_parser import _parse_structured_text


class PerceptorRequest(BaseModel):
    flavor: str
    params: dict = dict(temperature=0.01,
                        topK=10,
                        topP=0.9,
                        repetitionPenalty=1,
                        lengthPenalty=1,
                        penaltyAlpha=1,
                        maxLength=512)
    return_scores: bool = False

    @staticmethod
    def with_flavor(f: str):
        return PerceptorRequest(flavor=f)


class InstructionWithResult(BaseModel):
    """
    Original instruction text
    """
    instruction: str
    """
    True if the request was successful
    """
    is_success: bool
    """
    Response dictionary containing at least "text" element, containing response text.
    """
    response: dict = dict(text="")
    """
    Error text (if error occurred, otherwise "")
    """
    error_text: Optional[str] = ""

    @staticmethod
    def success(instruction: str, response: str):
        return InstructionWithResult(instruction=instruction,
                                     is_success=True,
                                     response=_parse_structured_text(response))

    @staticmethod
    def error(instruction: str, error_text: str):
        return InstructionWithResult(instruction=instruction,
                                     is_success=False,
                                     error_text=error_text)


class DocumentImageResult(BaseModel):
    """
    Zero based index of the original image/page
    """
    page_number: int
    """
    Instructions and corresponding results
    """
    instruction_results: Union[list[InstructionWithResult], InstructionWithResult]


@dataclass
class DocumentPageWithResult:
    """
    Zero based index of the original image/page
    """
    page_number: int
    """
    True if the request was successful
    """
    is_success: bool
    """
    Response dictionary containing at least "text" element, containing response text.
    """
    response: dict = field(default_factory=lambda: dict(text=""))
    """
    Error text (if error occurred, otherwise "")
    """
    error_text: Optional[str] = field(default_factory=lambda: "")


@dataclass
class InstructionWithPageResult:
    """
    Original instruction text
    """
    instruction: str

    """
    Pages and corresponding results
    """
    page_results: list[DocumentPageWithResult]
