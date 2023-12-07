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

import asyncio
import logging

from perceptor_client_lib.external_models import PerceptorRequest, InstructionWithResult
from perceptor_client_lib.utils import group_by_instruction
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

    print("results grouped by instruction:")

    mapped_result = group_by_instruction(result)
    for instruction_result in mapped_result:
        print(f"""instruction: {instruction_result.instruction}""")
        for page_result in instruction_result.page_results:
            if page_result.is_success:
                answer = page_result.response
            else:
                answer = f"error: {page_result}"
            print(f"""
                page: {page_result.page_number},
                answer: {answer}
                """)


asyncio.run(run_client_method())
