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

from perceptor_client_lib.external_models import PerceptorRequest
from tests_commons import create_client

logging.basicConfig(level=logging.DEBUG)

IMAGE_PATH = "../test_files/image_with_invoice_table.png"

perceptor_client = create_client()

req: PerceptorRequest = PerceptorRequest(flavor='original',
                                         params={
                                             "temperature": 0.5,
                                             "topK": 10,
                                             "topP": 0.9,
                                             "repetitionPenalty": 1,
                                             "lengthPenalty": 1,
                                             "penaltyAlpha": 1,
                                             "maxLength": 512
                                         })


async def run_client_method():
    result = await perceptor_client.ask_table_from_image(IMAGE_PATH,
                                                         instruction=
                                                         "GENERATE TABLE Artikelnummer, Beschreibung, Betrag GUIDED BY Betrag",
                                                         request_parameters=req
                                                         )

    if result.is_success:
        print(f"question '{result.instruction}', answer: '{result.response['text']}'")
    else:
        print(f"for question '{result.instruction}' following error occurred: {result.error_text}")


asyncio.run(run_client_method())
