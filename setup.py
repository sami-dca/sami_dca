# -*- coding: UTF8 -*-

import os
from setuptools import setup


def read(file_name: str) -> str:
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


def get_requirements(file_name: str) -> list:
    requirements_file = os.path.join(os.path.dirname(__file__), file_name)
    with open(requirements_file, 'r') as f:
        requirements = [r.strip() for r in f.readlines()]
    return requirements


setup(
    name="sami-dca",
    version="0.0",
    description="Sami, the decentralized communication application.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Lilian Boulard",
    author_email="lilian@boulard.fr",
    url="http://sami-dca.github.io/",
    download_url="https://github.com/sami-dca/sami_dca/releases/",
    license="MIT",
    install_requires=get_requirements("requirements.txt"),
    extras_require={
        "dev": get_requirements("requirements_dev.txt"),
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
    ],
    packages=[
        "sami"
    ],
    include_package_data=False
)
