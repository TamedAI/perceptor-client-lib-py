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

from typing import Union

from perceptor_client_lib.external_models import DocumentImageResult, InstructionWithResult, DocumentPageWithResult, \
    InstructionWithPageResult


def group_by_instruction(document_response_list: list[DocumentImageResult]) -> list[InstructionWithPageResult]:
    def get_as_list(inp: Union[InstructionWithResult, list[InstructionWithResult]]) -> list[InstructionWithResult]:
        if isinstance(inp, InstructionWithResult):
            return [inp]
        return inp

    if isinstance(document_response_list, list) and len(document_response_list) == 0:
        return []

    distinct_instructions = list(map(lambda ir: ir.instruction,
                                     get_as_list(document_response_list[0].instruction_results)))

    def get_instr_results_from(inst: str, d: DocumentImageResult):
        if isinstance(d.instruction_results, InstructionWithResult):
            first_found = d.instruction_results
        else:
            first_found = next(filter(lambda dr: dr.instruction == inst, d.instruction_results), None)

        if first_found is None:
            return None

        return DocumentPageWithResult(d.page_number, first_found.is_success, first_found.response,
                                      first_found.error_text)

    def get_pages_for_instruction(inst: str):
        mapped = list(map(lambda x: get_instr_results_from(inst, x), document_response_list))
        return InstructionWithPageResult(inst, mapped)

    return list(map(get_pages_for_instruction, distinct_instructions))
