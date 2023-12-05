from setuptools import setup
import os

BASE_VERSION_NUMBER = "0.6.1"


def get_ver_from_env():
    if 'GITHUB_RUN_ID' in os.environ:
        return ".dev" + os.environ['GITHUB_RUN_ID']
    return '.06'


# tmp
print("env_vars: ", os.environ)
# tmp

if os.environ.get('SOURCE_TAG'):
    version = os.environ['SOURCE_TAG']
else:
    version = BASE_VERSION_NUMBER + get_ver_from_env()

setup(
    version=version,
    name='perceptor_client_lib',
    license='LICENSE.TXT',
    description='Python Client for TamedAI Api',
    author='TamedAI GmbH',
    author_email='perceptor@tamed.ai',
    url='https://www.tamed.ai/',
    keywords=['TamedAI', 'IDP', 'Perceptor', 'LLM'],
    install_requires=[
        'annotated-types==0.5.0',
        'certifi==2023.7.22',
        'charset-normalizer==3.2.0',
        'idna==3.4',
        'pdf2image==1.16.3',
        'Pillow==10.0.1',
        'pydantic==2.3.0',
        'pydantic_core==2.6.3',
        'requests==2.31.0',
        'six==1.16.0',
        'sseclient-py==1.8.0',
        'tenacity==8.2.3',
        'typing_extensions==4.8.0',
        'urllib3==2.0.5'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache',
    ]
)
