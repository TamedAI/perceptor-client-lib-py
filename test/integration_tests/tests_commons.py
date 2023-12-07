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
import sys, os

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH, "..", "..", "src"
)

sys.path.append(SOURCE_PATH)
#
import perceptor_client_lib.perceptor as perceptor

_CONF_PATH = "config.json"
if os.path.exists(_CONF_PATH):
    with open(_CONF_PATH) as f:
        data = f.read()
    js = json.loads(data)
    api_key = js["TAI_PERCEPTOR_API_KEY"]
    api_url = js["TAI_PERCEPTOR_BASE_URL"]


def create_client():
    return perceptor.Client(api_key, api_url)
