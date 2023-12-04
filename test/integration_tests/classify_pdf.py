import asyncio
import logging

from perceptor_client_lib.external_models import PerceptorRequest, InstructionWithResult
from tests_commons import create_client

logging.basicConfig(level=logging.DEBUG)

DOCUMENT_PATH = "../test_files/pdf_with_2_pages.pdf"


def _get_answer(instr_result: InstructionWithResult):
    if instr_result.is_success:
        return f"response: {instr_result.response}"
    return f"error: {instr_result.error_text}"


async def run_client_method():
    perceptor_client = create_client()

    req: PerceptorRequest = PerceptorRequest(flavor="original",
                                             params={
                                                 "temperature": 0.01,
                                                 "topK": 10,
                                                 "topP": 0.9,
                                                 "repetitionPenalty": 1,
                                                 "lengthPenalty": 1,
                                                 "penaltyAlpha": 1,
                                                 "maxLength": 512
                                             })

    result = await perceptor_client.classify_document(DOCUMENT_PATH,
                                                      instruction="Was ist das für ein Dokument?",
                                                      classes=["Rechnung", "Schadensprotokoll", "Rezept"],
                                                      request_parameters=req
                                                      )

    for page_result in result:
        instruction_result: InstructionWithResult = page_result.instruction_results
        print(f"""
        page: {page_result.page_number}, 
        instruction: {instruction_result.instruction}, 
        answer: {_get_answer(instruction_result)}
        """)


asyncio.run(run_client_method())
