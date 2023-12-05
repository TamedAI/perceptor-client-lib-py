import unittest
from typing import Union

from perceptor_client_lib.utils import group_by_instruction
from perceptor_client_lib.external_models import DocumentImageResult, InstructionWithResult, InstructionWithPageResult


class UtilsTests(unittest.TestCase):
    @staticmethod
    def _create_instruction_with_result(instruction_text: str, page_number: int):
        return InstructionWithResult(
            instruction=instruction_text, is_success=1,
            response=dict(text="resp_" + instruction_text + "_page_" + str(page_number))
        )

    def _create_document_image_result(self, page_number: int, instructions: Union[str, list[str]]):
        if isinstance(instructions, str):
            return DocumentImageResult(page_number=page_number,
                                       instruction_results=
                                       self._create_instruction_with_result(instructions, page_number)
                                       )
        return DocumentImageResult(page_number=page_number,
                                   instruction_results=list(map(
                                       lambda i: self._create_instruction_with_result(i, page_number), instructions))
                                   )

    def test_multiple_pages_response_with_multiple_instructions_instructions_match(self):
        inst_1 = "first_inst"
        inst_2 = "second_inst"
        inst_3 = "third_inst"
        inst_4 = "fourth_inst"

        instructions = [inst_1, inst_2, inst_3, inst_4]

        to_map = [
            self._create_document_image_result(1, instructions),
            self._create_document_image_result(2, instructions),
            self._create_document_image_result(3, instructions),
        ]

        mapped = group_by_instruction(to_map)

        self.assertEqual(len(instructions), len(mapped))
        self.assertListEqual(list(map(lambda x: x.instruction, mapped)), instructions)
        for inst_group_resp in mapped:
            self.assertEqual(len(inst_group_resp.page_results), len(to_map))

    def test_multiple_pages_response_with_multiple_instructions_responses_match(self):
        inst_1 = "first_inst"
        inst_2 = "second_inst"
        inst_3 = "third_inst"
        inst_4 = "fourth_inst"

        instructions = [inst_1, inst_2, inst_3, inst_4]

        to_map = [
            self._create_document_image_result(1, instructions),
            self._create_document_image_result(2, instructions),
            self._create_document_image_result(3, instructions),
        ]

        all_responses = list(map(lambda ir: ir, [x for pr in to_map for x in pr.instruction_results]))

        mapped: list[InstructionWithPageResult] = group_by_instruction(to_map)

        for inst_group_resp in mapped:
            self.assertEqual(len(inst_group_resp.page_results), len(to_map))
            page_results = list(map(lambda r: r.response, inst_group_resp.page_results))
            to_compare = list(map(lambda r: r.response,
                               filter(lambda x: x.instruction == inst_group_resp.instruction, all_responses)))
            self.assertListEqual(page_results, to_compare)

    def test_multiple_pages_response_with_single_instruction(self):
        single_instruction = "single_instruction"

        to_map = [
            self._create_document_image_result(1, single_instruction),
            self._create_document_image_result(2, single_instruction),
            self._create_document_image_result(3, single_instruction),
        ]

        mapped: list[InstructionWithPageResult] = group_by_instruction(to_map)

        self.assertEqual(mapped[0].instruction, single_instruction)
        self.assertEqual(1, len(mapped))
        for inst_group_resp in mapped:
            self.assertEqual(len(inst_group_resp.page_results), len(to_map))

    def test_empty_pages_list_returns_empty_list(self):
        mapped = group_by_instruction([])
        self.assertEqual(0, len(mapped))


if __name__ == '__main__':
    unittest.main()
