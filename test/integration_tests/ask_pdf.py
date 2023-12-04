import asyncio
import logging

from perceptor_client_lib.external_models import PerceptorRequest, InstructionWithResult
from tests_commons import create_client

logging.basicConfig(level=logging.DEBUG)

DOCUMENT_PATH = "../test_files/pdf_with_2_pages.pdf"

perceptor_client = create_client()


def _get_answer(instr_result: InstructionWithResult):
    if instr_result.is_success:
        return f"response: {instr_result.response}"
    return f"error: {instr_result.error_text}"


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


async def run_client_method():
    result = await perceptor_client.ask_document(DOCUMENT_PATH,
                                                 instructions=[
                                                     "Vorname und Nachname des Kunden?",
                                                     "Ist der Kunde ein VIP? (Ja oder nein)",
                                                     "Was ist das für ein Dokument?"
                                                 ],
                                                 request_parameters=req
                                                 )

    for page_result in result:
        for instruction_result in page_result.instruction_results:
            print(f"""
            page: {page_result.page_number}, 
            instruction: {instruction_result.instruction}, 
            answer: {_get_answer(instruction_result)}
            """)


asyncio.run(run_client_method())