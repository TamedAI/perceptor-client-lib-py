import asyncio
import logging

from tests_commons import create_client
from perceptor_client_lib.external_models import PerceptorRequest

logging.basicConfig(level=logging.DEBUG)

TEXT_TO_PROCESS = """
Ich melde einen Schaden für meinen Kunden Hans. Er hatte einen Schaden durch eine Überschwemmung. 
Er hat Rechnungen in Höhe von 150000 Euro eingereicht. Der Schaden soll in 2 Chargen bezahlt werden. 
Seine  IBAN ist DE02300606010002474689. Versicherungsbeginn war der 01.10.2022. Er ist abgesichert bis 750.000 EUR. Der Ablauf der Versicherung ist der 01.10.2026. 
Der Kunde hat VIP-Kennzeichen und hatte schonmal einen Leitungswasserschaden in Höhe von 3840 Euro. 
Der Kunde möchte eine Antwort heute oder morgen erhalten. 
Der Schaden ist 2021 aufgetreten. Die Anschrift des Kunden ist: Berliner Straße 56, 60311 Frankfurt am Main.
Für Rückfragen möchte ich per Telefon kontaktiert werden. Es ist eine dringende Angelegenheit.
Meine Vermittlernumer ist die 090.100.
"""

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
    perceptor_client = create_client()

    result = await perceptor_client.ask_text(TEXT_TO_PROCESS,
                                             instructions=[
                                                 "Vorname und Nachname des Kunden?",
                                                 "Ist der Kunde ein VIP? (Ja oder nein)",
                                                 "was ist die IBAN?",
                                                 "Wie hoch sind seine Rechnungen?",
                                                 "Ist er abgesichert?",
                                                 "wann läuft die Versicherung ab?",
                                                 "wie wiele Chargen?",
                                                 "wie ist der Schaden entstanden?",
                                                 "wie lautet die Anschrift?",
                                                 "die Vermittlernummer?",
                                                 "hatte er schon mal Schaden?",
                                                 "wann will der Kunde Antwort?",
                                                 "wie soll ich kontaktiert werden?",
                                                 "ist es dringend?"
                                             ],
                                             request_parameters=req
                                             )

    for instruction_result in result:
        if instruction_result.is_success:
            print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response['text']}'")
        else:
            print(
                f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}")


asyncio.run(run_client_method())
