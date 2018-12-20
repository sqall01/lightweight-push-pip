import setuptools
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="lightweightpush",
    version=find_version("lightweightpush", "__init__.py"),
    author="Andre Pawlowski (sqall)",
    author_email="pypi-sqall@h4des.org",
    description="A simple, end-to-end encrypted and easy to use push service for messages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sqall01/lightweight-push-pip",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pycrypto"],
    package_data={"lightweightpush": "*.crt"},
)
