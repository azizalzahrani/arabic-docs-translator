"""
اختبارات طبقة الموفرين
Provider layer tests (no network access required).
"""

import pytest

from arabic_translator.providers import (
    BaseProvider,
    DryRunProvider,
    ProviderError,
    create_provider,
)


class _FlakyProvider(BaseProvider):
    """Provider that fails transiently before succeeding."""

    name = "flaky"

    def __init__(self, failures: int):
        super().__init__(model="test")
        self.failures = failures
        self.calls = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("rate limit exceeded")
        return "ok"


class TestCreateProvider:
    def test_none_provider(self):
        provider = create_provider("none")
        assert isinstance(provider, DryRunProvider)

    def test_auto_without_keys_falls_back_to_dry_run(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        provider = create_provider("auto")
        assert isinstance(provider, DryRunProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ProviderError):
            create_provider("gemini")

    def test_openai_without_key_raises(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        pytest.importorskip("openai")
        with pytest.raises(ProviderError):
            create_provider("openai")

    def test_env_provider_none(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "none")
        provider = create_provider("auto")
        assert isinstance(provider, DryRunProvider)


class TestDryRunProvider:
    def test_returns_user_prompt(self):
        provider = DryRunProvider()
        assert provider.complete("system", "the text") == "the text"


class TestRetry:
    @pytest.fixture(autouse=True)
    def _no_sleep(self, monkeypatch):
        import arabic_translator.providers as providers_module
        monkeypatch.setattr(providers_module.time, "sleep", lambda _s: None)

    def test_retries_transient_errors(self):
        provider = _FlakyProvider(failures=2)
        assert provider.complete_with_retry("s", "u", retries=2) == "ok"
        assert provider.calls == 3

    def test_gives_up_after_retries(self):
        provider = _FlakyProvider(failures=10)
        with pytest.raises(ProviderError):
            provider.complete_with_retry("s", "u", retries=1)
