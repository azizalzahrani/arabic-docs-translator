"""
طبقة موفري نماذج اللغة
LLM provider layer.

تجريد موحد لاستدعاء OpenAI أو Anthropic، مع وضع تجريبي آمن بدون اتصال
Unified abstraction for calling OpenAI or Anthropic, with a safe offline dry-run mode.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

#: Default model per provider. Override via env vars or constructor arguments.
#: Check your provider's documentation for the latest available model names.
DEFAULT_MODELS = {
    "openai": os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o"),
    "anthropic": os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-sonnet-4-6"),
}

_RETRYABLE_MESSAGES = ("rate limit", "overloaded", "timeout", "temporarily", "529", "503")


class ProviderError(RuntimeError):
    """خطأ في طبقة الموفر | Raised when an LLM provider cannot be used."""


class BaseProvider:
    """واجهة موفر أساسية | Base provider interface."""

    name = "base"

    def __init__(self, model: Optional[str] = None, temperature: float = 0.3):
        self.model = model
        self.temperature = temperature

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """إرسال طلب والحصول على النص | Send a request and return the text reply."""
        raise NotImplementedError

    def complete_with_retry(self, system_prompt: str, user_prompt: str, retries: int = 2) -> str:
        """استدعاء مع إعادة محاولة بسيطة | Call with simple retry on transient failures."""
        last_error: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                return self.complete(system_prompt, user_prompt)
            except Exception as exc:  # noqa: BLE001 - provider SDKs raise many types
                last_error = exc
                message = str(exc).lower()
                transient = any(token in message for token in _RETRYABLE_MESSAGES)
                if attempt < retries and transient:
                    wait = 2 ** attempt
                    logger.warning(
                        "Transient %s error (attempt %d/%d), retrying in %ds: %s",
                        self.name, attempt + 1, retries + 1, wait, exc,
                    )
                    time.sleep(wait)
                    continue
                raise ProviderError(f"{self.name} request failed: {exc}") from exc
        raise ProviderError(f"{self.name} request failed: {last_error}")


class DryRunProvider(BaseProvider):
    """
    موفر تجريبي بدون اتصال — يعيد النص الأصلي كما هو
    Offline dry-run provider — returns the source text unchanged.

    يُستخدم عند غياب مفاتيح API حتى لا يتلف المستند بنص وهمي.
    Used when no API key is configured so documents are never corrupted
    with placeholder text. Structure handling can still be tested end to end.
    """

    name = "none"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # The user prompt is the source text itself (see TranslatorAgent).
        return user_prompt


class OpenAIProvider(BaseProvider):
    """موفر OpenAI | OpenAI chat-completions provider."""

    name = "openai"

    def __init__(self, model: Optional[str] = None, temperature: float = 0.3,
                 api_key: Optional[str] = None):
        super().__init__(model or DEFAULT_MODELS["openai"], temperature)
        try:
            from openai import OpenAI  # lazy import
        except ImportError as exc:
            raise ProviderError(
                "The 'openai' package is required for the OpenAI provider. "
                "Install it with: pip install openai"
            ) from exc

        key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ProviderError("OPENAI_API_KEY is not set.")
        self._client = OpenAI(api_key=key)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        return (content or "").strip()


class AnthropicProvider(BaseProvider):
    """موفر Anthropic | Anthropic messages provider."""

    name = "anthropic"

    def __init__(self, model: Optional[str] = None, temperature: float = 0.3,
                 api_key: Optional[str] = None):
        super().__init__(model or DEFAULT_MODELS["anthropic"], temperature)
        try:
            import anthropic  # lazy import
        except ImportError as exc:
            raise ProviderError(
                "The 'anthropic' package is required for the Anthropic provider. "
                "Install it with: pip install anthropic"
            ) from exc

        key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            raise ProviderError("ANTHROPIC_API_KEY is not set.")
        self._client = anthropic.Anthropic(api_key=key)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
        return "".join(parts).strip()


def create_provider(
    provider: str = "auto",
    model: Optional[str] = None,
    temperature: float = 0.3,
    api_key: Optional[str] = None,
) -> BaseProvider:
    """
    إنشاء موفر LLM
    Create an LLM provider.

    Args:
        provider: "openai" | "anthropic" | "none" | "auto".
            "auto" picks based on LLM_PROVIDER env var, then available API keys,
            and falls back to the offline dry-run provider with a warning.
        model: اسم النموذج (اختياري — لكل موفر قيمة افتراضية)
        temperature: درجة العشوائية
        api_key: مفتاح صريح يتجاوز متغيرات البيئة

    Returns:
        BaseProvider: الموفر الجاهز للاستخدام
    """
    normalized = (provider or "auto").strip().lower()
    if model in ("", "auto"):
        model = None

    if normalized == "auto":
        env_provider = os.getenv("LLM_PROVIDER", "").strip().lower()
        if env_provider in ("openai", "anthropic", "none"):
            normalized = env_provider
        elif os.getenv("OPENAI_API_KEY"):
            normalized = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            normalized = "anthropic"
        else:
            logger.warning(
                "No LLM API key found (OPENAI_API_KEY / ANTHROPIC_API_KEY). "
                "Running in dry-run mode: documents are processed but NOT translated."
            )
            normalized = "none"

    if normalized == "openai":
        return OpenAIProvider(model=model, temperature=temperature, api_key=api_key)
    if normalized == "anthropic":
        return AnthropicProvider(model=model, temperature=temperature, api_key=api_key)
    if normalized in ("none", "dry-run", "dryrun", "offline"):
        return DryRunProvider(model=model or "dry-run", temperature=temperature)

    raise ProviderError(
        f"Unknown provider '{provider}'. Expected one of: openai, anthropic, none, auto."
    )
