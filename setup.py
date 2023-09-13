"""Setup file."""
import re
from pathlib import Path
from typing import Any

from setuptools import setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Environment :: Console",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 2 :: Only",
    "Programming Language :: Python :: 2.7",
    "Topic :: System :: Systems Administration",
    "Topic :: Database",
    "Topic :: Text Processing",
    "Topic :: Internet",
    "Topic :: Utilities",
]


def read_file(*paths: Any) -> str:
    """Read a file."""
    here = Path(Path(__file__).resolve()).parent
    with Path(Path(here, *paths)).open() as f:
        return f.read()


src_file = read_file("es2csv_cli.py")
url = "https://github.com/nikhilbadyal/es2csv"


def get_version() -> str:
    """Pull version from module without loading module first.

    This was lovingly collected and adapted from
    https://github.com/pypa/virtualenv/blob/12.1.1/setup.py#L67.
    """
    if version_match := re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        src_file,
        re.M,
    ):
        return version_match.group(1)
    msg = "Unable to find version string."
    raise RuntimeError(msg)


def get_description() -> str:
    """Get the description of the package."""
    try:
        return src_file.split("\n")[2].split(":")[1].strip()
    except Exception as e:
        msg = "Unable to find description string."
        raise RuntimeError(msg) from e


version = get_version()

with Path("README.rst").open() as file_readme:
    readme = file_readme.read()
    readme = re.sub(r".(/docs/[A-Z]+.rst)", rf"{url}/blob/{version}\1", readme)

with Path("docs/HISTORY.rst").open() as history_file:
    history = history_file.read()

with Path("requirements.txt").open() as file_requirements:
    requirements = file_requirements.read().splitlines()

settings: Any = {}
settings.update(
    name="es2csv",
    version=version,
    description=get_description(),
    long_description=f"{readme}\n\n{history}",
    author="Taras Layshchuk",
    author_email="taraslayshchuk@gmail.com",
    license="Apache 2.0",
    url=url,
    classifiers=classifiers,
    python_requires="==2.7.*",
    keywords="elasticsearch export kibana es bulk csv",
    py_modules=["es2csv", "es2csv_cli"],
    entry_points={"console_scripts": ["es2csv = es2csv_cli:main"]},
    install_requires=requirements,
)

setup(**settings)
