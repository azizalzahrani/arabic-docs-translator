"""
مترجم التوثيقات التقنية للعربية
Arabic Documentation Translator

Multi-agent pipeline for translating developer documentation from English to Arabic.
"""

from .pipeline import DocumentTranslator, BatchTranslator
from .config import Config
from .glossary import GlossaryManager

__version__ = "0.1.0"
__author__ = "Aziz Al-Zahrani"
__license__ = "MIT"

__all__ = [
    "DocumentTranslator",
    "BatchTranslator",
    "Config",
    "GlossaryManager",
]
