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
