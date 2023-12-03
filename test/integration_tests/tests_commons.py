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
