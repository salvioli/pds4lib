#!/usr/bin/env python3
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pds4lib',
    version='0.0.1',
    author='Federico Salvioli',
    author_email='salvioli.federico@gmail.com',
    packages=['pds4lib'],
    scripts=['pds4lib/bin/update_pds4_collection.py'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='LICENSE.txt',
    description='PDS 4 python library to conveniently work with PDS4 data',
    install_requires=[
        "lxml",
        "pathlib", 'chardet'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)