import unittest
from requests import Response
from perceptor_client_lib.perceptor_repository import _PerceptorRepositoryHttpClient


class PerceptorRepositoryHttpClientTests(unittest.TestCase):

    @staticmethod
    def _create_bytes_from_text(input_text: str):
        b = bytearray()
        b.extend(map(ord, input_text))
        return b

    def test_parse_response_json_text(self):
        error_text_expected = "Wrong instruction format"

        response: Response = Response()
        response._content = self._create_bytes_from_text(f'{{"detail":"{error_text_expected}"}}')
        res = _PerceptorRepositoryHttpClient._parse_bad_response_text(response)
        self.assertEqual(res.error_text, error_text_expected)

    def test_parse_response_text(self):
        error_text_expected = "Wrong instruction format"

        response: Response = Response()
        response._content = self._create_bytes_from_text(error_text_expected)
        res = _PerceptorRepositoryHttpClient._parse_bad_response_text(response)
        self.assertEqual(res.error_text, error_text_expected)


if __name__ == '__main__':
    unittest.main()
