from dataclasses import dataclass
from pathlib import Path
from re import MULTILINE
from re import search
from typing import List

from setuptools import find_packages
from setuptools import setup


@dataclass
class MetaData:
    name: str
    version: str
    description: str
    long_description: str
    install_requires: List[str]


def _get_metadata() -> MetaData:
    with open("README.md") as file:
        contents = file.read()
    if (match_1 := search(r"^# ([\w-]+)", contents, flags=MULTILINE)) is None:
        raise ValueError("Unable to determine 'name'")
    name = match_1.group(1)
    if (match_2 := search("^## Overview", contents, flags=MULTILINE)) is None:
        raise ValueError("Unable to determine start of 'description'")
    long_description = contents[match_2.end() :].strip("\n")
    if (match_3 := search("^## ", long_description, flags=MULTILINE)) is None:
        raise ValueError("Unable to determine end of 'description'")
    description = long_description[: match_3.start()].replace("\n", " ").strip("\n")
    root = Path(__file__).resolve().parent
    with open(
        path := root.joinpath(name.replace("-", "_"), "__init__.py"),
    ) as file:
        if (
            match := search(
                r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]$',
                file.read(),
                MULTILINE,
            )
        ) is not None:
            version = match.group(1)
        else:
            raise ValueError(f"Unable to determine 'version' from {path}")
    with open(root.joinpath("requirements.txt")) as file:
        install_requires = file.read().strip().split("\n")
    return MetaData(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        install_requires=install_requires,
    )


_METADATA = _get_metadata()


setup(
    name=_METADATA.name,
    version=_METADATA.version,
    author="Derek Wan",
    author_email="d.wan@icloud.com",
    url="https://github.com/dycw/writer-cm/",
    download_url="https://pypi.org/project/writer-cm/",
    license="MIT",
    description=_METADATA.description,
    long_description=_METADATA.long_description,
    long_description_content_type="text/markdown",
    install_requires=_METADATA.install_requires,
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
)
