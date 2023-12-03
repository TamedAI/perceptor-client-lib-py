from io import BufferedReader
from typing import Optional
from os import environ

import perceptor_client_lib.perceptor_repository
from perceptor_client_lib.content_session import process_contents
from perceptor_client_lib.external_models import PerceptorRequest, InstructionWithResult, DocumentImageResult
from perceptor_client_lib.image_parsing import convert_image_to_contextdata, parse_multiple_images
from perceptor_client_lib.internal_models import *
from perceptor_client_lib.pdf_parsing import get_images_from_document_pages
from perceptor_client_lib.perceptor_repository import _PerceptorRepositoryHttpClient, \
    PerceptorRepositoryHttpClientSettings
from perceptor_client_lib.perceptor_repository_retrydecorator import _PerceptorRepositoryRetryDecorator

_ENV_VAR_BASE_URL = "TAI_PERCEPTOR_BASE_URL"
_ENV_VAR_API_KEY = "TAI_PERCEPTOR_API_KEY"


def _get_value_or_env_fallback(val: Optional[str], env_key: str):
    if val is None or len(val) == 0:
        return environ.get(env_key)
    return val


def _assert_required_parameters(api_key: str, api_url: str):
    def _get_error_message(val: str, name: str):
        if val is None or len(val.strip()) == 0:
            return f"missing '{name}'"
        return ""

    api_key_message = _get_error_message(api_key, "api_key")
    api_url_message = _get_error_message(api_url, "request_url")
    message = ", ".join(filter(lambda x: x is not None and len(x) > 0, [api_url_message, api_key_message]))
    if len(message) > 0:
        raise ValueError(f"Invalid configuration: {message}")
    pass


class Client:
    """
    TamedAI client for the api.
    """

    def __init__(self, api_key: str = None,
                 request_url: str = None,
                 wait_timeout: int = 60,
                 max_level_of_parallelization: int = 10,
                 max_retries: int = 3,
                 thread_delay_factor: float = 0.005):
        """
        Creates Client instance
        :param api_key: api key to use.
        :param request_url: request url.
        :param wait_timeout: timeout for request (in seconds), default is 60s
        :param max_retries: number of retries for failed retryable requests
        :param thread_delay_factor: delay (in seconds) between parallel request
        """

        api_key_val = _get_value_or_env_fallback(api_key, _ENV_VAR_API_KEY)
        request_url_val = _get_value_or_env_fallback(request_url, _ENV_VAR_BASE_URL)
        _assert_required_parameters(api_key_val, request_url_val)

        http_client = _PerceptorRepositoryHttpClient(
            PerceptorRepositoryHttpClientSettings(
                api_key=api_key_val,
                request_url=request_url_val,
                wait_timeout=wait_timeout
            ))
        decorated_client = _PerceptorRepositoryRetryDecorator(http_client, max_retries=max_retries)
        self._repository: perceptor_client_lib.perceptor_repository._PerceptorRepository = decorated_client
        self._max_level_of_parallelization = max_level_of_parallelization
        self._thread_delay_factor: float = thread_delay_factor

    def ask_text(self, text_to_process: str,
                 instructions: list[str], request_parameters: PerceptorRequest) \
            -> list[InstructionWithResult]:
        """
        Sends instruction(s) for the specified text
        :param text_to_process: text to be processed.
        :param instructions: instruction(s) to perform on text.
        :param request_parameters: request parameters.
        :return: list of tuples containing instruction and InstructionResult.
                InstructionResult can be either text or instance of InstructionError.
        """
        return process_contents(self._repository,
                                TextContextData(text_to_process),
                                request_parameters,
                                InstructionMethod.QUESTION,
                                instructions,
                                [],
                                self._max_level_of_parallelization,
                                self._thread_delay_factor
                                )

    def classify_text(self,
                      text_to_process: str,
                      instruction: str,
                      classes: list[str],
                      request_parameters: PerceptorRequest) -> InstructionWithResult:
        """
        Sends classify instruction for the specified text
        :param text_to_process: text to be processed.
        :param instruction: instruction to perform on text.
        :param classes: list of classes ("document", "invoice" etc.)
        :param request_parameters: request parameters.
        :return: tuple containing original instruction and InstructionResult.
        """
        return process_contents(self._repository,
                                TextContextData(text_to_process),
                                request_parameters,
                                InstructionMethod.CLASSIFY,
                                instruction,
                                classes,
                                self._max_level_of_parallelization,
                                self._thread_delay_factor
                                )

    def ask_image(self, image: Union[str, bytes, BufferedReader],
                  instructions: list[str],
                  request_parameters: PerceptorRequest,
                  file_type: Optional[str] = None) -> list[InstructionWithResult]:
        """
        Sends instruction(s) for the specified image
        :param image: image to be processed. Either a path to file, opened file handle, or bytearray.
        :param instructions: instruction(s) to perform on the image.
        :param request_parameters: request parameters.
        :param file_type: mandatory if image specified as handle or bytearray, must be either 'png' or 'jpg'.
        :return: list of tuples containing instruction and InstructionResult.
                InstructionResult can be either text or instance of InstructionError.
        """
        image_content_data = convert_image_to_contextdata(image, file_type=file_type)
        return process_contents(self._repository,
                                image_content_data,
                                request_parameters,
                                InstructionMethod.QUESTION,
                                instructions,
                                [],
                                self._max_level_of_parallelization,
                                self._thread_delay_factor
                                )

    def classify_image(self, image: Union[str, bytes, BufferedReader],
                       instruction: str,
                       classes: list[str],
                       request_parameters: PerceptorRequest,
                       file_type: Optional[str] = None) -> InstructionWithResult:
        """
        Sends classify instruction for the specified image
        :param image: image to be processed. Either a path to file, opened file handle, or bytearray.
        :param instruction: instruction to perform on the image.
        :param classes: list of classes ("document", "invoice" etc.)
        :param request_parameters: request parameters.
        :param file_type: mandatory if image specified as handle or bytearray, must be either 'png' or 'jpg'.
        :return: tuple containing original instruction and InstructionResult.
        """
        return process_contents(self._repository,
                                convert_image_to_contextdata(image, file_type=file_type),
                                request_parameters,
                                InstructionMethod.CLASSIFY,
                                instruction,
                                classes,
                                self._max_level_of_parallelization,
                                self._thread_delay_factor
                                )

    def ask_table_from_image(self, image: Union[str, bytes, BufferedReader],
                             instruction: str,
                             request_parameters: PerceptorRequest,
                             file_type: Optional[str] = None
                             ) -> InstructionWithResult:
        """
        Sends a table instruction for the specified image.
        :param image: image to be processed. Either a path to file, opened file handle, or bytearray
        :param instruction: instruction to perform, for example 'GENERATE TABLE Article, Amount, Value GUIDED BY Value'
        :param request_parameters: request parameters.
        :param file_type: mandatory if image specified as handle or bytearray, must be either 'png' or 'jpg'.
        :return: tuple containing original instruction and InstructionResult.
        """
        image_content_data = convert_image_to_contextdata(image, file_type=file_type)
        return process_contents(self._repository,
                                image_content_data,
                                request_parameters,
                                InstructionMethod.TABLE,
                                instruction,
                                [],
                                self._max_level_of_parallelization,
                                self._thread_delay_factor
                                )

    def ask_document(self, pdf_doc: Union[str, bytes, BufferedReader],
                     instructions: list[str],
                     request_parameters: PerceptorRequest) \
            -> list[DocumentImageResult]:
        """
        Sends instruction(s) for the specified pdf document.
        :param pdf_doc: document to be processed. Either a path to file, opened file handle, or bytearray
        :param instructions: instruction(s) to perform on the document.
        :param request_parameters: request parameters.
        :return: list (corresponding to document pages), with list of tuples containing
            instruction and InstructionResult.
        """

        return self._extract_and_process_images_from_document(pdf_doc, instructions, [], InstructionMethod.QUESTION,
                                                              request_parameters)

    def classify_document(self, pdf_doc: Union[str, bytes, BufferedReader],
                          instruction: str,
                          classes: list[str],
                          request_parameters: PerceptorRequest) \
            -> list[DocumentImageResult]:
        """
        Sends classify instruction for the specified pdf document.
        :param pdf_doc: document to be processed. Either a path to file, opened file handle, or bytearray
        :param instruction: instruction to perform on the image.
        :param classes: list of classes ("document", "invoice" etc.)
        :param request_parameters: request parameters.
        :return: list (corresponding to document pages), with list of tuples containing
            instruction and InstructionResult.
        """
        return self._extract_and_process_images_from_document(pdf_doc, instruction, classes, InstructionMethod.CLASSIFY,
                                                              request_parameters)

    def ask_document_images(self, image_list: Union[list[str], list[(bytes, str)], list[(BufferedReader, str)]],
                            instructions: list[str],
                            request_parameters: PerceptorRequest
                            ) -> list[DocumentImageResult]:
        """
        Sends instruction(s) for the specified document's images.
        :param image_list: document images to be processed. Either list of file paths,
         or list of tuples (bytes, file extension) or list of tuples (BufferedReader, file extension).
        :param instructions: instruction(s) to perform on the document.
        :param request_parameters: request parameters.
        :return: list (corresponding to document pages), with list of tuples containing
            instruction and InstructionResult.
        """
        return self._ask_document_images(image_list,
                                         instructions,
                                         [],
                                         InstructionMethod.QUESTION,
                                         request_parameters)

    def classify_document_images(self, image_list: Union[list[str], list[(bytes, str)], list[(BufferedReader, str)]],
                                 instruction: str,
                                 classes: list[str],
                                 request_parameters: PerceptorRequest
                                 ) -> list[DocumentImageResult]:
        """
        Sends classify instruction for the specified images.
        :param image_list: document images to be processed. Either list of file paths,
         or list of tuples (bytes, file extension) or list of tuples (BufferedReader, file extension).
        :param instruction: instruction to perform on the document.
        :param classes: list of classes ("document", "invoice" etc.)
        :param request_parameters: request parameters.
        :return: list (corresponding to images), with list of tuples containing
            instruction and InstructionResult.
        """
        return self._ask_document_images(image_list,
                                         instruction,
                                         classes,
                                         InstructionMethod.CLASSIFY,
                                         request_parameters)

    def ask_table_from_document(self, pdf_doc: Union[str, bytes, BufferedReader],
                                instruction: str,
                                request_parameters: PerceptorRequest) -> list[DocumentImageResult]:
        """
        Sends a table instruction for the specified document.
        :param pdf_doc: document to be processed. Either a path to file, opened file handle, or bytearr
        :param instruction: instruction to perform, for example 'GENERATE TABLE Article, Amount, Value GUIDED BY Value'
        :param request_parameters: request parameters.
        :return: list (corresponding to document pages), wish tuples containing original
            instruction and InstructionResult. InstructionResult can be either text or instance of InstructionError.
        """
        return self._extract_and_process_images_from_document(pdf_doc, instruction, [], InstructionMethod.TABLE,
                                                              request_parameters)

    def ask_table_from_document_images(self,
                                       image_list: Union[list[str], list[(bytes, str)], list[(BufferedReader, str)]],
                                       instruction: str,
                                       request_parameters: PerceptorRequest
                                       ) -> list[DocumentImageResult]:
        """
        Sends a table instruction for the specified document's images.
        :param image_list: document images to be processed. Either list of file paths,
         or list of tuples (bytes, file extension) or list of tuples (BufferedReader, file extension).
        :param instruction: instruction to perform, for example 'GENERATE TABLE Article, Amount, Value GUIDED BY Value'
        :param request_parameters: refined request parameters.
        :return: list (corresponding to document pages), wish tuples containing original
            instruction and InstructionResult. InstructionResult can be either text or instance of InstructionError.
        """
        return self._ask_document_images(image_list,
                                         instruction,
                                         [],
                                         InstructionMethod.TABLE,
                                         request_parameters)

    def _extract_and_process_images_from_document(self, pdf_doc: Union[str, bytes, BufferedReader],
                                                  instruction: Union[str, list[str]],
                                                  classes: list[str],
                                                  method: InstructionMethod,
                                                  request_parameters) \
            -> Union[list[InstructionWithResult], list[DocumentImageResult]]:
        images = get_images_from_document_pages(pdf_doc)

        def map_image_func(i):
            return i, "png"

        mapped_images = list(map(map_image_func, images))
        return self._ask_document_images(mapped_images,
                                         instruction,
                                         classes,
                                         method,
                                         request_parameters)

    def _ask_document_images(self, image_list: Union[list[str], list[(bytes, str)], list[(BufferedReader, str)]],
                             instructions: Union[str, list[str]],
                             classes: list[str],
                             method: InstructionMethod,
                             request_parameters: PerceptorRequest,
                             ) -> list[DocumentImageResult]:
        mapped_images = parse_multiple_images(image_list)
        return process_contents(self._repository,
                                mapped_images,
                                request_parameters,
                                method,
                                instructions,
                                classes,
                                self._max_level_of_parallelization,
                                self._thread_delay_factor
                                )
