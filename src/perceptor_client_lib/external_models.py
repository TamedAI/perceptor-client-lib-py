from typing import Union, Optional

from pydantic import BaseModel

from perceptor_client_lib.structured_response_parser import parse_structured_text


class PerceptorRequest(BaseModel):
    flavor: str
    params: dict = {}
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
                                     response=parse_structured_text(response))

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
