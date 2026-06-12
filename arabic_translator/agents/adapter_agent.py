"""
وكيل التكييف والتوطين
Adapter and Localization Agent.

يكيّف تعليقات الأكواد والمحتوى للغة والثقافة العربية
Adapts code comments and content for Arabic language and culture.
"""

import re
from typing import Dict, List, Optional, Tuple

from ..parsers import CodeBlockHandler
from ..glossary import GlossaryManager

# Segments that must never be touched by adaptation:
# inline code, markdown link/image targets, bare URLs, and pipeline placeholders.
_PROTECTED_PATTERN = re.compile(
    r'(`[^`\n]+`'                 # inline code
    r'|\]\([^)\s]+\)'             # markdown link/image target: ](url)
    r'|https?://\S+'              # bare URLs
    r'|__[A-Z][A-Z0-9_]*?_\d+__'  # placeholders like __CODE_BLOCK_1__ / __MDX_PLACEHOLDER_2__
    r')'
)

_ARABIC_CHAR = r'[؀-ۿ]'


class AdapterAgent:
    """
    وكيل التكييف والتوطين
    Adapter and localization agent class.

    يكيّف الترجمات ويعريبها ثقافياً
    Adapts translations and localizes them culturally.
    """

    def __init__(
        self,
        glossary_manager: Optional[GlossaryManager] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        تهيئة وكيل التكييف
        Initialize adapter agent.

        Args:
            glossary_manager: مدير القاموس
            api_key: مفتاح API (غير مستخدم حالياً — الوكيل قاعدي)
            model: نموذج اللغة (غير مستخدم حالياً — الوكيل قاعدي)
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.code_handler = CodeBlockHandler()
        self.api_key = api_key
        self.model = model

    def adapt_translation(self, translated: str, original: str = "") -> str:
        """
        تكييف الترجمة
        Adapt translation for Arabic conventions.

        يحمي الأكواد المضمنة والروابط والعناصر النائبة قبل أي تعديل.
        Inline code, URLs, and placeholders are protected before any change.

        Args:
            translated: النص المترجم
            original: النص الأصلي (اختياري للسياق)

        Returns:
            str: النص المكيّف
        """
        if not translated:
            return translated

        protected_text, protected_segments = self._protect_segments(translated)

        adapted = protected_text
        adapted = self._adapt_grammar(adapted)
        adapted = self._adapt_punctuation(adapted)
        adapted = self._adapt_spacing(adapted)

        return self._restore_segments(adapted, protected_segments)

    def _protect_segments(self, text: str) -> Tuple[str, Dict[str, str]]:
        """حماية المقاطع الحساسة | Shield code spans, URLs, and placeholders."""
        segments: Dict[str, str] = {}

        def replace(match: "re.Match[str]") -> str:
            token = f'\x00ADAPT{len(segments)}\x00'
            segments[token] = match.group(0)
            return token

        return _PROTECTED_PATTERN.sub(replace, text), segments

    @staticmethod
    def _restore_segments(text: str, segments: Dict[str, str]) -> str:
        """استعادة المقاطع المحمية | Restore shielded segments."""
        for token, segment in segments.items():
            text = text.replace(token, segment)
        return text

    def adapt_code_comments(
        self,
        code: str,
        language: str = "javascript",
        translator_func=None
    ) -> str:
        """
        تكييف تعليقات الأكواد
        Adapt code comments.

        Args:
            code: كود البرنامج
            language: لغة البرمجة
            translator_func: دالة ترجمة اختيارية تُطبق قبل التكييف

        Returns:
            str: الكود مع التعليقات المكيّفة
        """
        def process(comment: str) -> str:
            if translator_func:
                comment = translator_func(comment)
            return self._adapt_comment(comment)

        return self.code_handler.translate_comments_in_code(code, language, process)

    def _adapt_comment(self, comment: str) -> str:
        """تكييف تعليق واحد"""
        adapted = self._adapt_grammar(comment)
        adapted = self._ensure_proper_spacing(adapted)
        return adapted

    def _adapt_grammar(self, text: str) -> str:
        """
        تكييف قواعد اللغة
        Fix common machine-translation grammar slips.

        ملاحظة: لا يتم حذف الهمزات أو تغيير رسم الحروف — إزالة الهمزة
        تُفسد الإملاء العربي الصحيح (تُستخدم للتطبيع في البحث فقط).
        Note: hamza forms are intentionally left untouched. Stripping hamzas
        corrupts correct Arabic orthography; that kind of normalization
        belongs in search/matching, never in produced text.
        """
        adapted = text

        patterns = [
            (r'يمكنك ب ?اضافة', 'يمكنك إضافة'),
            (r'يمكنك ب ?استخدام', 'يمكنك استخدام'),
            (r'يتم ب ?الضغط', 'يتم الضغط'),
            (r'قم ب ?ال(\w+)', r'قم بال\1'),
        ]

        for pattern, replacement in patterns:
            adapted = re.sub(pattern, replacement, adapted)

        return adapted

    def _adapt_punctuation(self, text: str) -> str:
        """
        تكييف الترقيم
        Use Arabic punctuation only in Arabic context.

        تُستبدل الفاصلة والفاصلة المنقوطة وعلامة الاستفهام بالعربية فقط
        عندما تجاور حروفاً عربية، فلا تتأثر الأرقام (1,000) ولا النصوص الإنجليزية.
        Latin punctuation is converted only when adjacent to Arabic characters,
        so numbers like 1,000 and English fragments stay intact.
        """
        adapted = text

        # Comma: convert when the preceding character is Arabic.
        adapted = re.sub(f'({_ARABIC_CHAR}),', r'\1،', adapted)
        # Semicolon: same rule.
        adapted = re.sub(f'({_ARABIC_CHAR});', r'\1؛', adapted)
        # Question mark: when the sentence before it ends with Arabic.
        adapted = re.sub(f'({_ARABIC_CHAR}\\s*)\\?', r'\1؟', adapted)

        return adapted

    def _adapt_spacing(self, text: str) -> str:
        """
        تكييف المسافات
        Normalize spacing without destroying line structure.
        """
        # Collapse runs of spaces/tabs but PRESERVE newlines
        adapted = re.sub(r'[ \t]+', ' ', text)
        # Trim trailing spaces per line
        adapted = re.sub(r' +(\n|$)', r'\1', adapted)
        # No space before Arabic punctuation
        adapted = re.sub(r' +([،؛؟])', r'\1', adapted)
        return adapted

    def _ensure_proper_spacing(self, text: str) -> str:
        """ضمان مسافات صحيحة"""
        text = text.rstrip()
        text = re.sub(r'[ \t]+', ' ', text)
        return text

    def apply_glossary_terms(self, text: str) -> str:
        """
        تطبيق مصطلحات القاموس على البقايا الإنجليزية
        Replace leftover standalone English glossary terms in translated text.

        لا تُمس المقاطع المحمية (أكواد، روابط، عناصر نائبة).
        Protected segments (code, URLs, placeholders) are never modified.
        """
        protected_text, segments = self._protect_segments(text)
        adapted = protected_text

        terms = self.glossary_manager.glossaries.get('tech', {})
        for term, translation in terms.items():
            if len(term) <= 2:
                continue
            pattern = r'(?<![\w`])' + re.escape(term) + r'(?![\w`])'
            adapted = re.sub(pattern, translation, adapted, flags=re.IGNORECASE)

        return self._restore_segments(adapted, segments)

    def localize_cultural_references(self, text: str) -> str:
        """
        توطين الإشارات الثقافية
        Localize cultural references.
        """
        localized = text

        adaptations = {
            r'\bAmerica\b': 'أمريكا',
            r'\bEurope\b': 'أوروبا',
            r'\bJanuary\b': 'يناير',
            r'\bFebruary\b': 'فبراير',
            r'\bMarch\b': 'مارس',
            r'\bApril\b': 'أبريل',
            r'\bMay\b': 'مايو',
            r'\bJune\b': 'يونيو',
            r'\bJuly\b': 'يوليو',
            r'\bAugust\b': 'أغسطس',
            r'\bSeptember\b': 'سبتمبر',
            r'\bOctober\b': 'أكتوبر',
            r'\bNovember\b': 'نوفمبر',
            r'\bDecember\b': 'ديسمبر',
        }

        for pattern, replacement in adaptations.items():
            localized = re.sub(pattern, replacement, localized)

        return localized

    def validate_adaptation(self, original: str, adapted: str) -> Dict:
        """
        التحقق من التكييف
        Validate adaptation.
        """
        issues = []

        if len(adapted) < len(original) * 0.5:
            issues.append("Adapted text is significantly shorter")
        if len(adapted) > len(original) * 2.0:
            issues.append("Adapted text is significantly longer")

        if adapted.count('(') != adapted.count(')'):
            issues.append("Unmatched parentheses")
        if adapted.count('[') != adapted.count(']'):
            issues.append("Unmatched brackets")

        if not self._is_valid_arabic(adapted):
            issues.append("No Arabic characters detected")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'original_length': len(original),
            'adapted_length': len(adapted),
        }

    def _is_valid_arabic(self, text: str) -> bool:
        """التحقق من احتواء النص على حروف عربية"""
        return bool(re.search(_ARABIC_CHAR, text))

    def batch_adapt(self, translations: List[str]) -> List[str]:
        """
        تكييف مجموعة من الترجمات
        Adapt multiple translations.
        """
        return [self.adapt_translation(t) for t in translations]

    def get_adaptation_report(self) -> Dict:
        """الحصول على تقرير التكييف"""
        return {
            'status': 'ready',
            'supported_languages': ['javascript', 'python', 'typescript', 'java', 'c', 'cpp'],
            'features': [
                'Grammar adaptation',
                'Context-aware Arabic punctuation',
                'Code/URL/placeholder protection',
                'Cultural localization',
            ],
        }
