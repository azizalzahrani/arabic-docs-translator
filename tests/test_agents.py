"""
اختبارات الوكلاء
Agent tests: reviewer, adapter, and translator (offline).
"""

import pytest

from arabic_translator.agents import AdapterAgent, ReviewerAgent, TranslatorAgent
from arabic_translator.providers import DryRunProvider


class TestReviewerAgent:
    """اختبارات وكيل المراجعة"""

    @pytest.fixture
    def reviewer(self):
        return ReviewerAgent()

    def test_review_does_not_crash_with_code_fences(self, reviewer):
        """Regression: review_translation used to raise TypeError (len of int)."""
        original = "Use this:\n```python\nprint(1)\n```\n"
        translated = "استخدم هذا:\n```python\nprint(1)\n```\n"
        report = reviewer.review_translation(original, translated)
        assert report["technical_accuracy"] == 1.0

    def test_review_detects_missing_code_block(self, reviewer):
        original = "Text\n```js\nlet a = 1;\n```\n"
        translated = "نص بدون كود"
        report = reviewer.review_translation(original, translated)
        assert any("Code block count mismatch" in issue for issue in report["issues"])

    def test_untranslated_terms_whole_words_only(self, reviewer):
        # 'state' inside 'useState' must not be flagged
        found = reviewer._find_untranslated_terms("استخدم useState هنا")
        assert "state" not in found

    def test_untranslated_terms_ignores_inline_code(self, reviewer):
        found = reviewer._find_untranslated_terms("استخدم `function` هنا")
        assert "function" not in found


class TestAdapterAgent:
    """اختبارات وكيل التكييف"""

    @pytest.fixture
    def adapter(self):
        return AdapterAgent()

    def test_keeps_hamza_intact(self, adapter):
        """Regression: hamzas used to be stripped, corrupting Arabic output."""
        text = "أضِف المكوّن إلى المشروع وسؤال وهيئة"
        assert adapter.adapt_translation(text) == text

    def test_urls_never_modified(self, adapter):
        text = "راجع https://example.com?a=1,b;c وأيضاً [الدليل](https://a.b/c?x=1,2)"
        adapted = adapter.adapt_translation(text)
        assert "https://example.com?a=1,b;c" in adapted
        assert "(https://a.b/c?x=1,2)" in adapted

    def test_numbers_keep_latin_separators(self, adapter):
        adapted = adapter.adapt_translation("التكلفة 1,000.50 دولار")
        assert "1,000.50" in adapted

    def test_inline_code_protected(self, adapter):
        adapted = adapter.adapt_translation("استخدم `useState, useEffect` هنا")
        assert "`useState, useEffect`" in adapted

    def test_arabic_punctuation_in_arabic_context(self, adapter):
        adapted = adapter.adapt_translation("مرحباً, كيف الحال?")
        assert "مرحباً،" in adapted
        assert adapted.endswith("؟")

    def test_newlines_preserved(self, adapter):
        adapted = adapter.adapt_translation("السطر الأول\nالسطر الثاني")
        assert "\n" in adapted

    def test_placeholders_protected(self, adapter):
        adapted = adapter.adapt_translation("نص __CODE_BLOCK_1__ ونص __MDX_PLACEHOLDER_2__")
        assert "__CODE_BLOCK_1__" in adapted
        assert "__MDX_PLACEHOLDER_2__" in adapted


class TestTranslatorAgent:
    """اختبارات وكيل الترجمة (بدون اتصال)"""

    @pytest.fixture
    def agent(self):
        return TranslatorAgent(llm=DryRunProvider())

    def test_dry_run_returns_source_text_exactly(self, agent):
        assert agent.is_dry_run
        text = "The useState hook adds state."
        assert agent.translate_text(text) == text

    def test_empty_text(self, agent):
        assert agent.translate_text("") == ""
        assert agent.translate_text("   ") == ""

    def test_translation_memory(self, agent):
        first = agent.translate_text("Hello world")
        second = agent.translate_text("Hello world")
        assert first == second
        assert agent.get_stats()["total_translations"] == 1

    def test_glossary_context_includes_known_terms(self, agent):
        context = agent._build_glossary_context("The component state changed")
        assert "component" in context.lower()

    def test_stats_include_provider(self, agent):
        stats = agent.get_stats()
        assert stats["provider"] == "none"
