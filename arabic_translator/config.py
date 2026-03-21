"""
إعدادات التطبيق
Configuration module for Arabic Documentation Translator.

يدير جميع الإعدادات والمتغيرات البيئية
Manages all configuration and environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Config(BaseModel):
    """
    فئة الإعدادات الرئيسية
    Main configuration class.

    تحتوي على جميع إعدادات التطبيق من متغيرات البيئة
    Contains all application settings from environment variables.
    """

    # LLM Configuration
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"))

    # Model Configuration
    translation_model: str = Field(default_factory=lambda: os.getenv("TRANSLATION_MODEL", "gpt-4"))
    review_model: str = Field(default_factory=lambda: os.getenv("REVIEW_MODEL", "gpt-4"))
    adapter_model: str = Field(default_factory=lambda: os.getenv("ADAPTER_MODEL", "gpt-4"))

    # Translation Settings
    quality_threshold: float = Field(default_factory=lambda: float(os.getenv("QUALITY_THRESHOLD", "0.8")))
    glossary_strict: bool = Field(default_factory=lambda: os.getenv("GLOSSARY_STRICT", "true").lower() == "true")
    preserve_markdown: bool = Field(default_factory=lambda: os.getenv("PRESERVE_MARKDOWN", "true").lower() == "true")
    translate_code_comments: bool = Field(default_factory=lambda: os.getenv("TRANSLATE_CODE_COMMENTS", "true").lower() == "true")

    # Paths
    output_dir: str = Field(default_factory=lambda: os.getenv("OUTPUT_DIR", "./translated_docs"))
    glossary_dir: str = Field(default_factory=lambda: os.getenv("GLOSSARY_DIR", "./glossary"))
    log_dir: str = Field(default_factory=lambda: os.getenv("LOG_DIR", "./logs"))

    # Batch Processing
    max_workers: int = Field(default_factory=lambda: int(os.getenv("MAX_WORKERS", "4")))
    batch_size: int = Field(default_factory=lambda: int(os.getenv("BATCH_SIZE", "10")))

    # Language Settings
    target_language: str = Field(default_factory=lambda: os.getenv("TARGET_LANGUAGE", "ar"))
    source_language: str = Field(default_factory=lambda: os.getenv("SOURCE_LANGUAGE", "en"))
    dialect: str = Field(default_factory=lambda: os.getenv("DIALECT", "ar_SA"))

    # Logging
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    debug_mode: bool = Field(default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true")

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True

    def validate_api_keys(self) -> bool:
        """
        التحقق من وجود مفاتيح API المطلوبة
        Validate that required API keys are present.

        Returns:
            bool: True إذا كانت جميع المفاتيح موجودة، False وإلا
        """
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")

        return True

    def ensure_directories(self) -> None:
        """
        إنشاء المجلدات المطلوبة إن لم تكن موجودة
        Create required directories if they don't exist.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.glossary_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def to_dict(self) -> dict:
        """
        تحويل الإعدادات إلى قاموس
        Convert configuration to dictionary.

        Returns:
            dict: Dictionary representation of config
        """
        return self.model_dump()


# Create global config instance
config = Config()
