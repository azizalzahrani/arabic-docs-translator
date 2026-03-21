"""
وكيل التكييف والتوطين
Adapter and Localization Agent.

يكيّف تعليقات الأكواد والمحتوى للغة والثقافة العربية
Adapts code comments and content for Arabic language and culture.
"""

from typing import Dict, Optional, List
import re
from ..parsers import CodeBlockHandler
from ..glossary import GlossaryManager


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
        model: str = "gpt-4"
    ):
        """
        تهيئة وكيل التكييف
        Initialize adapter agent.

        Args:
            glossary_manager: مدير القاموس
            api_key: مفتاح API
            model: نموذج اللغة
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.code_handler = CodeBlockHandler()
        self.api_key = api_key
        self.model = model

    def adapt_translation(self, translated: str, original: str = "") -> str:
        """
        تكييف الترجمة
        Adapt translation for cultural localization.

        Args:
            translated: النص المترجم
            original: النص الأصلي (اختياري للسياق)

        Returns:
            str: النص المكيّف
        """
        adapted = translated

        # Apply various adaptations
        adapted = self._adapt_grammar(adapted)
        adapted = self._adapt_terminology(adapted)
        adapted = self._adapt_punctuation(adapted)
        adapted = self._adapt_spacing(adapted)
        adapted = self._remove_unnecessary_markers(adapted)

        return adapted

    def adapt_code_comments(
        self,
        code: str,
        language: str = "javascript"
    ) -> str:
        """
        تكييف تعليقات الأكواد
        Adapt code comments.

        Args:
            code: كود البرنامج
            language: لغة البرمجة

        Returns:
            str: الكود مع التعليقات المكيّفة
        """
        return self.code_handler.translate_comments_in_code(
            code,
            language,
            self._adapt_comment
        )

    def _adapt_comment(self, comment: str) -> str:
        """تكييف تعليق واحد"""
        adapted = comment

        # Remove unnecessary markers
        adapted = self._remove_unnecessary_markers(adapted)

        # Apply grammar adaptation
        adapted = self._adapt_grammar(adapted)

        # Ensure proper spacing and punctuation
        adapted = self._ensure_proper_spacing(adapted)

        return adapted

    def _adapt_grammar(self, text: str) -> str:
        """تكييف قواعد اللغة"""
        adapted = text

        # Fix common issues
        # Replace "ال" articles appropriately
        patterns = [
            (r'يمكنك ب اضافة', 'يمكنك إضافة'),
            (r'يمكنك ب استخدام', 'يمكنك استخدام'),
            (r'يتم ب الضغط', 'يتم الضغط'),
        ]

        for pattern, replacement in patterns:
            adapted = re.sub(pattern, replacement, adapted)

        # Fix hamza issues
        adapted = adapted.replace('آ', 'ا')  # Normalize alef variations
        adapted = adapted.replace('أ', 'ا')
        adapted = adapted.replace('ؤ', 'و')
        adapted = adapted.replace('ئ', 'ي')

        return adapted

    def _adapt_terminology(self, text: str) -> str:
        """تكييف المصطلحات"""
        adapted = text

        # Apply glossary translations
        for term, translation in self.glossary_manager.glossaries.get('tech', {}).items():
            # Be careful with whole word replacement
            pattern = r'\b' + re.escape(term) + r'\b'
            adapted = re.sub(pattern, translation, adapted, flags=re.IGNORECASE)

        return adapted

    def _adapt_punctuation(self, text: str) -> str:
        """تكييف الترقيم"""
        adapted = text

        # Use Arabic punctuation marks
        adapted = adapted.replace('.', '.')  # Arabic period (same as English)
        adapted = adapted.replace(',', '،')  # Arabic comma
        adapted = adapted.replace(';', '؛')  # Arabic semicolon
        adapted = adapted.replace('?', '؟')  # Arabic question mark
        adapted = adapted.replace('!', '!')  # Keep exclamation (same)

        return adapted

    def _adapt_spacing(self, text: str) -> str:
        """تكييف المسافات"""
        adapted = text

        # Remove extra spaces
        adapted = re.sub(r'\s+', ' ', adapted)

        # Ensure proper spacing around Arabic punctuation
        adapted = re.sub(r'\s+([،؛؟])', r'\1', adapted)

        return adapted

    def _ensure_proper_spacing(self, text: str) -> str:
        """ضمان مسافات صحيحة"""
        # Remove trailing spaces
        text = text.rstrip()

        # Ensure single spaces between words
        text = re.sub(r'\s+', ' ', text)

        return text

    def _remove_unnecessary_markers(self, text: str) -> str:
        """إزالة العلامات غير الضرورية"""
        adapted = text

        # Remove duplicate markers
        adapted = adapted.replace('((', '(')
        adapted = adapted.replace('))', ')')
        adapted = adapted.replace('[[', '[')
        adapted = adapted.replace(']]', ']')

        return adapted

    def localize_cultural_references(self, text: str) -> str:
        """
        توطين الإشارات الثقافية
        Localize cultural references.

        Args:
            text: النص المراد توطينه

        Returns:
            str: النص المعرّب ثقافياً
        """
        localized = text

        # Common cultural adaptations
        adaptations = {
            r'\bAmerica\b': 'أمريكا',
            r'\bEurope\b': 'أوروبا',
            r'\bJanuary\b': 'يناير',
            r'\bFebruary\b': 'فبراير',
            r'\bMarch\b': 'مارس',
            r'\bApril\b': 'أبريل',
            r'\bMay\b': 'مايو',
            r'\bJune\b': 'يونيو',
        }

        for pattern, replacement in adaptations.items():
            localized = re.sub(pattern, replacement, localized, flags=re.IGNORECASE)

        return localized

    def validate_adaptation(self, original: str, adapted: str) -> Dict:
        """
        التحقق من التكييف
        Validate adaptation.

        Args:
            original: النص الأصلي المترجم
            adapted: النص المكيّف

        Returns:
            dict: نتائج التحقق
        """
        issues = []

        # Check length similarity
        if len(adapted) < len(original) * 0.5:
            issues.append("Adapted text is significantly shorter")
        if len(adapted) > len(original) * 2.0:
            issues.append("Adapted text is significantly longer")

        # Check for unmatched brackets/parentheses
        if adapted.count('(') != adapted.count(')'):
            issues.append("Unmatched parentheses")
        if adapted.count('[') != adapted.count(']'):
            issues.append("Unmatched brackets")

        # Check for proper Arabic text
        if not self._is_valid_arabic(adapted):
            issues.append("Invalid Arabic characters detected")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'original_length': len(original),
            'adapted_length': len(adapted),
        }

    def _is_valid_arabic(self, text: str) -> bool:
        """التحقق من صحة النص العربي"""
        # Check if text contains valid Arabic characters
        arabic_pattern = r'[\u0600-\u06FF]'
        return bool(re.search(arabic_pattern, text))

    def batch_adapt(self, translations: List[str]) -> List[str]:
        """
        تكييف مجموعة من الترجمات
        Adapt multiple translations.

        Args:
            translations: قائمة الترجمات

        Returns:
            list: قائمة الترجمات المكيّفة
        """
        return [self.adapt_translation(t) for t in translations]

    def get_adaptation_report(self) -> Dict:
        """الحصول على تقرير التكييف"""
        return {
            'status': 'ready',
            'supported_languages': ['javascript', 'python', 'typescript', 'fastapi'],
            'features': [
                'Grammar adaptation',
                'Terminology consistency',
                'Punctuation adaptation',
                'Cultural localization',
            ],
        }
