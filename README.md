# Perceptor Python Client

## Installing package

Setup a virtual environment and run the following command to install the latest version:

```bash
pip install perceptor-client-lib@git+https://github.com/TamedAI/perceptor-client-lib-py
```

## Installing _poppler_
If you want to use pdf processing functionality, [follow this instructions](https://pypi.org/project/pdf2image/) to install _popppler_ on your machine.
On Windows, if the poppler "bin" path is not added to PATH, you have to set the environment variable POPPLER_PATH to point to _bin_.

## Usage


Create the client first:
```python
perceptor_client = perceptor.Client(api_key="your_key",request_url="request_url")
```

It is also possible to create _Client_ without specifying any parameters. In that case, following environment variables
will be used automatically:<br>
_TAI_PERCEPTOR_BASE_URL_ for api url
_TAI_PERCEPTOR_API_KEY_ for api key

If no configuration parameters are specified and the above mentioned env variables are missing then a _ValueError_ exception
will be raised.


### Creating request parameters

Parameters are specified via _PerceptorRequest_ class.
The structure of _PerceptorRequest_:

&emsp;_flavor_ specifies request "flavor", for example "original". It's a mandatory value and has to be specified.

&emsp;_params_ is a dictionary of additional parameters, for example:
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


Create request object specifying only the _flavor_ value:

```python
request = PerceptorRequest.with_flavor("flavor_name")
```

Create request object specifying all the parameters explicitly:
```python
request = PerceptorRequest(flavor="original", params={
    "temperature": 0.01,
    "topK": 10,
    "topP": 0.9,
    "repetitionPenalty": 1,
    "lengthPenalty": 1,
    "penaltyAlpha": 1,
    "maxLength": 512
})

```

Create request object with parameters and to include return scores:
```python
request = PerceptorRequest(flavor="original", return_scores=True, params={
    "temperature": 0.01,
    "topK": 10,
    "topP": 0.9,
    "repetitionPenalty": 1,
    "lengthPenalty": 1,
    "penaltyAlpha": 1,
    "maxLength": 512
})

```

### Sending instructions for text

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

### Sending instructions for an image

Following image formats are supported: "_jpg_", "_png_".

From image file:
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

or from image file:
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

or from bytes:
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

### Sending instructions for a pdf document

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


### Sending classify instructions for text

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

### Reading responses

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

## Mapping response
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