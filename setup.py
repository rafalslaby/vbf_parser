import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="vbf-parser",
    version="1.2.0",
    description="Parse vbf to dict",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rafalslaby/vbf_parser",
    author="Rafal Slaby",
    author_email="rafal.slaby222@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["vbf_parser"],
    include_package_data=True,
)
