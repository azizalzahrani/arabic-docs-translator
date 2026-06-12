from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="arabic-docs-translator",
    version="0.2.0",
    author="Aziz Al-Zahrani",
    author_email="contact@azizalzahrani.dev",
    description="Multi-agent pipeline for translating developer documentation to Arabic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/azizalzahrani/arabic-docs-translator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "openai": ["openai>=1.30.0"],
        "anthropic": ["anthropic>=0.30.0"],
        "all": ["openai>=1.30.0", "anthropic>=0.30.0"],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
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
