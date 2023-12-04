import asyncio
import os
import unittest

import perceptor_client_lib.pdf_parsing as pdf_parsing

_pdf_path = os.path.join(os.path.dirname(__file__), "test_files", "pdf_with_2_pages.pdf")
NUMBER_OF_PAGES_IN_DOCUMENT = 2


class PdfParsingTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_images_from_file_path(self):
        result = await asyncio.create_task(pdf_parsing.get_images_from_document_pages(_pdf_path))
        self.assertEqual(len(result), NUMBER_OF_PAGES_IN_DOCUMENT)
        for b in result:
            self.assertGreater(len(b), 0)

    def test_read_images_from_pages_from_opened_document(self):
        buffered_reader = open(_pdf_path, 'rb')
        with buffered_reader:
            result = asyncio.run(pdf_parsing.get_images_from_document_pages(buffered_reader))
        self.assertEqual(len(result), NUMBER_OF_PAGES_IN_DOCUMENT)

    def test_read_images_from_pages_from_bytes(self):
        buffered_reader = open(_pdf_path, 'rb')
        with buffered_reader:
            file_bytes = buffered_reader.read()
            result = asyncio.run(pdf_parsing.get_images_from_document_pages(file_bytes))

        self.assertEqual(len(result), NUMBER_OF_PAGES_IN_DOCUMENT)


if __name__ == '__main__':
    unittest.main()
