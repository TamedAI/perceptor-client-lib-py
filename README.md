# Perceptor Client

![Perceptor](perceptor_paper_stack.png)

Perceptor is a multi modal large language model (LLM) focused on extracting information from document images or text. 

## Quickstart

Get your API token by [signing in](https://platform.tamed.ai) and go to the API tab.

```python
import perceptor_client_lib.perceptor as perceptor

perceptor_client = perceptor.Client(api_key="API_TOKEN_HERE", request_url="https://perceptor-api.tamed.ai/1/model/")

context = """
    Greetings traveler, my name is Perceptor. I was born in 2022 and I generate text from text or image context. Therefore, I am able to extract  information from documents. Just ask.
"""

instructions = [
    "When was Perceptor born?",
    "What can Perceptor do?",
]

result = perceptor_client.ask_text(context, instructions=instructions, request_parameters=perceptor.PerceptorRequest(flavor="original"))

for instruction_result in result:
    if instruction_result.is_success:
        print(f"Q: '{instruction_result.instruction}'\nA: '{instruction_result.response}'\n------")
    else:
        print(f"For question '{instruction_result.instruction}' the following error occurred: {instruction_result.error_text}")
```

## Installation

Setup a virtual environment and run the following command to install the latest version:

```bash
pip install perceptor-client-lib@git+https://github.com/TamedAI/perceptor-client-lib-py
```

### Dependencies

- (optional) _Poppler_: If you want to use pdf processing functionality, [follow this instructions](https://pypi.org/project/pdf2image/) to install _popppler_ on your machine.
On Windows, if the poppler "bin" path is not added to PATH, you have to set the environment variable POPPLER_PATH to point to _bin_.

## Usage

### Create client

```python
perceptor_client = perceptor.Client(api_key="your_key",request_url="request_url")
```

It is also possible to create _Client_ without specifying any parameters. In that case, following environment variables
will be used automatically:

- _TAI_PERCEPTOR_BASE_URL_ for api url
- _TAI_PERCEPTOR_API_KEY_ for api key

If no configuration parameters are specified and the above mentioned env variables are missing, a _ValueError_ exception will be raised.

### Request parameters

Parameters are specified via _PerceptorRequest_ class.
The structure of _PerceptorRequest_:

- _flavor_ specifies request "flavor", for example "original". It's a mandatory value and has to be specified. You can find more information about flavors [here](#flavor).
- _params_ is a dictionary of additional generation parameters, for example:
```python
{
    "temperature": 0.01,
    "topK": 10,
    "topP": 0.9,
    "repetitionPenalty": 1,
    "lengthPenalty": 1,
    "penaltyAlpha": 1,
    "maxLength": 512
}
```
- _return_scores_ controls the access to confident scores:
```python
request = PerceptorRequest(flavor="original", return_scores=True)
```

### Asynchronous access

The perceptor client supports async access.

```python
result = await perceptor_client.ask_text("text_to_process", instructions=["Question 1?"], request_parameters=request)
```

### Ask text

```python
result = await perceptor_client.ask_text("text_to_process",
                                       instructions=[
                                           "Question 1?",
                                           "Question 2",
                                       ],
                                   request_parameters=request)

for instruction_result in result:
    if instruction_result.is_success:
        print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response['text']}'")
    else:
        print(f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}"

```

### Ask image

Following image formats are supported: "_jpg_", "_png_".

From image path:
```python
result = await perceptor_client.ask_image("path_to_image_file",
                                       instructions=[
                                           "Question 1?",
                                           "Question 2",
                                       ],
                                        request_parameters=request)

for instruction_result in result:
    if instruction_result.is_success:
        print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response['text']}'")
    else:
        print(f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}"

```

...or from image file:

```python

reader = open("image_path", 'rb')
with reader:
    result = await perceptor_client.ask_image(reader,
                                       instructions=[
                                           "Question 1?",
                                           "Question 2",
                                       ], file_type='jpg',
                                        request_parameters=request)

for instruction_result in result:
    if instruction_result.is_success:
        print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response['text']}'")
    else:
        print(f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}"
```

...or from bytes:
```python

reader = open(_image_path, 'rb')
with reader:
    content_bytes = reader.read()
    result = await perceptor_client.ask_image(content_bytes,
                                       instructions=[
                                           "Question 1?",
                                           "Question 2",
                                       ], file_type='jpg',
                                        request_parameters=request)
for instruction_result in result:
    if instruction_result.is_success:
        print(f"question '{instruction_result.instruction}', answer: '{instruction_result.response['text']}'")
    else:
        print(f"for question '{instruction_result.instruction}' following error occurred: {instruction_result.error_text}"
```

Table queries can be performed as following:
```python

result = await perceptor_client.ask_table_from_image("path_to_image_file",
                                       instruction="GENERATE TABLE Column1, Column2, Column3 GUIDED BY Column3",
                                               request_parameters=request
                                               )
```

### Ask PDF document

From document file:
```python
result = await perceptor_client.ask_document("path_to_document_file",
                                       instructions=[
                                           "Question 1?",
                                           "Question 2",
                                       ],
                                       request_parameters=request)

if result.is_success:
    print(f"question '{result.instruction}', answer: '{result.response['text']}'")
else:
    print(f"for question '{result.instruction}' following error occurred: {result.error_text}")

```

### Classify text

```python
result = await perceptor_client.classify_text("text_to_process",
                                        instruction="What kind of document is it?",
                                        classes=["invoice", "application"],
                                        request_parameters=request)

if result.is_success:
    print(f"question '{result.instruction}', answer: '{result.response['scores']}'")
else:
    print(f"for question '{result.instruction}' following error occurred: {result.error_text}")
```

### Read response

Basic class containing the processing result is _InstructionWithResult_ ([see here](/src/perceptor_client_lib/external_models.py)).

It contains following properties:<br>
_instruction_ contains the original instruction text<br>
_is_success_  set to True if the query was successful<br>
_response_ is a dictionary containing at least "text" element (with actual response text) and may contain additional values (for example scores).
<br>__NOTE__: the "classify..." methods return empty "text" and "scores" corresponding to the specified _classes_.<br>
_error_text_ error text (if error occurred)

Following methods return the list of _InstructionWithResult_ instances:<br>
_ask_text_<br>
_ask_image_<br>

Following method(s) return single _InstructionWithResult_ instance:<br> 
_ask_table_from_image_<br>
_classify_text_<br>
_classify_image_<br>
_classify_document_<br>
_classify_document_images_<br>

Following methods query multiple images (document images), hence return the list of [_DocumentImageResult_](/src/perceptor_client_lib/external_models.py) instances, containing,
beside the _InstructionWithResult_ list, also the original page info:<br>
_ask_document_<br>
_ask_document_images_<br>
_ask_table_from_document_<br>
_ask_table_from_document_images_<br>

### Map response
If you use the methods returning the list of _DocumentImageResult_ and need to have the responses grouped by instruction
rather than page, you can use the provided utility function to map the response:

```python
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
```

## Flavor

A flavor is the specialization of the Perceptor model for a specific instruction set. 
Usually, a flavor is created for a specific document type (e.g. invoices).
With a custom flavor the model performance can be increased dramatically.
At the same time, confidence scores are better aligned with correct answers.

```python
request = perceptor.PerceptorRequest(flavor="MY_FLAVOR")
result = perceptor_client.ask_text("context text...", instructions=["Question 1", "Question 2"], request_parameters=request)
```

To create your own flavor you will need a small dataset (>50 documents) together with your instruction set and the correct answers. 
Upload your dataset [here](https://platform.tamed.ai/app/data) and [reach out](mailto:sales@tamed.ai) to us to  access your custom flavor.

## Links

- [API documentation](https://platform.tamed.ai/app/api)
- [Flavor training](https://platform.tamed.ai/app/data)
- [Homepage](https://tamed.ai)
