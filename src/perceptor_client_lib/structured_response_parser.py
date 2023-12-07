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
