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

result = perceptor_client.ask_image(IMAGE_PATH,
                                    instructions=[
                                        "What is the invoice number?",
                                        "What is the invoice date?",
                                        "To whom is the invoice billed?",
                                        "What is the project number?",
                                        "What is the cost center?",
                                        "What is the purchase order?",
                                        "What is the identification?",
                                        "Who rendered services?",
                                        "Is it reissued invoice?",
                                        "Project authorization number?"
                                    ],
                                    request_parameters=req
                                    )

for instruction_result in result:
    if instruction_result.is_success:
        print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response['text']}'")
    else:
        print(f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}")

