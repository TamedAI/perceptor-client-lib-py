import unittest

from perceptor_client_lib.content_session import _ContentSession, process_contents
from perceptor_client_lib.external_models import PerceptorRequest, \
    DocumentImageResult, InstructionWithResult
from perceptor_client_lib.internal_models import PerceptorRepositoryRequest, TextContextData, InstructionContextData, \
    ImageContextData, InstructionMethod, _InstructionResult, InstructionError, ClassifyEntry
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


class ContentSessionTests(unittest.TestCase):

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

    def test_all_contents_are_processed_with_all_instructions(self):
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

        result = process_contents(_mock_repository,
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
            rep: DocumentImageResult = r
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
            process_contents(_mock_repository,
                             data_contexts,
                             self._create_default_request(),
                             InstructionMethod.CLASSIFY,
                             instructions,
                             classify_entries=["x"],
                             max_number_of_threads=1,
                             thread_delay_factor=0
                             )
        self.assertRaises(ValueError, _call_method)



if __name__ == '__main__':
    unittest.main()
