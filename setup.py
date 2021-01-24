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
        long_description = file.read()
    first, _, second, *_ = long_description.splitlines()
    if (match := search(r"^# ([\w-]+)$", first)) is not None:
        name = match.group(1)
    else:
        raise ValueError(f"Unable to determine 'name' from line {first!r}")
    if (match := search(r"^(.+)$", second)) is not None:
        description = match.group(1)
    else:
        raise ValueError(f"Unable to determine 'description' from {second!r}")
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
