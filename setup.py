from setuptools import setup

setup(
    name="md-generator",
    packages=["md_generator"],
    version="1.0.0",
    install_requires=[
        "jinja2>=3.1.2",
        "markdown2>=2.4.10",
        "importlib-metadata; python_version == '3.11'",
    ],
)