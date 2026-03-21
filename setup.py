from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="arabic-docs-translator",
    version="0.1.0",
    author="Aziz Al-Zahrani",
    author_email="contact@azizalzahrani.dev",
    description="Multi-agent pipeline for translating developer documentation to Arabic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/azizalzahrani/arabic-ai-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "arabic-translate=arabic_translator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "arabic_translator": [
            "glossary/*.json",
        ],
    },
)
