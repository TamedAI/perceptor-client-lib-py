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

import io
import os
from typing import Union, Optional

from pdf2image import convert_from_path, convert_from_bytes


def _get_poppler_path() -> Optional[str]:
    resolved_path = os.environ.get('POPPLER_PATH', None)
    if resolved_path is not None and not os.path.isabs(resolved_path):
        return os.path.join(os.getcwd(), resolved_path)
    return resolved_path


async def get_images_from_document_pages(file: Union[str, io.BufferedReader, bytes]) -> list[bytes]:
    poppler_path = _get_poppler_path()

    def get_bytes_from_image(im):
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    def get_images():
        if isinstance(file, io.BufferedReader):
            file_bytes = file.read()
            return convert_from_bytes(file_bytes, poppler_path=poppler_path)

        if isinstance(file, bytes):
            return convert_from_bytes(file, poppler_path=poppler_path)

        return convert_from_path(file, poppler_path=poppler_path)

    images = get_images()

    mapped = list(map(get_bytes_from_image, images))

    return mapped
