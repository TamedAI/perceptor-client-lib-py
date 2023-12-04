import json
from json import JSONDecodeError

_KEY_NAME_TEXT: str = "text"


def _parse_structured_text(to_parse: str) -> dict:
    def create_dictionary_with_text():
        return dict(text=to_parse)

    if len(to_parse.strip()) == 0:
        return create_dictionary_with_text()

    try:
        result: dict = json.loads(to_parse)
        if isinstance(result, dict):
            if result.get(_KEY_NAME_TEXT) is None:
                result[_KEY_NAME_TEXT] = ""
            return result
        return create_dictionary_with_text()
    except JSONDecodeError:
        return create_dictionary_with_text()
