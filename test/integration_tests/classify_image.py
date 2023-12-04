import asyncio
import logging
from tests_commons import create_client
from perceptor_client_lib.external_models import PerceptorRequest

logging.basicConfig(level=logging.DEBUG)

IMAGE_PATH = "../test_files/invoice.jpg"

perceptor_client = create_client()

req: PerceptorRequest = PerceptorRequest(flavor="original", return_scores=True, params={
    "temperature": 0.01,
    "topK": 10,
    "topP": 0.9,
    "repetitionPenalty": 1,
    "lengthPenalty": 1,
    "penaltyAlpha": 1,
    "maxLength": 512
})


async def run_client_method():
    instruction_result = await perceptor_client.classify_image(IMAGE_PATH,
                                                               instruction="Was ist das für ein Dokument?",
                                                               classes=["Rechnung", "Antrag", "Rezept"],
                                                               request_parameters=req
                                                               )

    if instruction_result.is_success:
        print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response}'")
    else:
        print(
            f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}")


asyncio.run(run_client_method())
