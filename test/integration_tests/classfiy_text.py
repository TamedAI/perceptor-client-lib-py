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

TEXT_TO_PROCESS = """
Ich melde einen Schaden für meinen Kunden Hans Mustermann. Er hatte einen Schaden durch eine Überschwemmung. 
Er hat Rechnungen in Höhe von 150000 Euro eingereicht. Der Schaden soll in 2 Chargen bezahlt werden. 
Seine  IBAN ist DE02300606010002474689. Versicherungsbeginn war der 01.10.2022. Er ist abgesichert bis 750.000 EUR. Der Ablauf der Versicherung ist der 01.10.2026. 
Der Kunde hat VIP-Kennzeichen und hatte schonmal einen Leitungswasserschaden in Höhe von 3840 Euro. 
Der Kunde möchte eine Antwort heute oder morgen erhalten. 
Der Schaden ist 2021 aufgetreten. Die Anschrift des Kunden ist: Leipzigertr. 12, 21390 Bonn.
Für Rückfragen möchte ich per Telefon kontaktiert werden. Es ist eine dringende Angelegenheit.
Meine Vermittlernumer ist die 090.100.
"""

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

class_to_ask = [
    "versicherung",
    "Schadenmeldung",
    "letter",
    "brief"
]


async def run_client_method():
    result = await perceptor_client.classify_text(TEXT_TO_PROCESS,
                                                  instruction="was ist das für ein Text?",
                                                  request_parameters=req,
                                                  classes=class_to_ask)

    if result.is_success:
        print(f"question '{result.instruction}', answer: '{result.response['scores']}'")
    else:
        print(f"for question '{result.instruction}' following error occurred: {result.error_text}")


asyncio.run(run_client_method())
