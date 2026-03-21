"""
أدوات معالجة النصوص
Text processing utilities.

يوفر وظائف مساعدة لمعالجة النصوص والمحتوى
Provides helper functions for text processing and content handling.
"""

import re
from typing import List, Tuple, Dict, Optional


class TextUtils:
    """
    فئة أدوات معالجة النصوص
    Text utilities class.

    توفر وظائف مساعدة لمعالجة النصوص والمحتوى العربي والإنجليزي
    Provides helper functions for processing Arabic and English text.
    """

    # Regular expressions for text detection
    ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]+')
    ENGLISH_PATTERN = re.compile(r'[a-zA-Z]+')
    CODE_BLOCK_PATTERN = re.compile(
        r'```(?:[\w]+)?\n(.*?)\n```',
        re.DOTALL
    )
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')

    @staticmethod
    def is_arabic(text: str) -> bool:
        """
        التحقق من احتواء النص على أحرف عربية
        Check if text contains Arabic characters.

        Args:
            text: النص المراد التحقق منه

        Returns:
            bool: True إذا كان يحتوي على أحرف عربية
        """
        return bool(TextUtils.ARABIC_PATTERN.search(text))

    @staticmethod
    def is_english(text: str) -> bool:
        """
        التحقق من احتواء النص على أحرف إنجليزية
        Check if text contains English characters.

        Args:
            text: النص المراد التحقق منه

        Returns:
            bool: True إذا كان يحتوي على أحرف إنجليزية
        """
        return bool(TextUtils.ENGLISH_PATTERN.search(text))

    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """
        استخراج كتل الكود من النص
        Extract code blocks from text.

        Args:
            text: النص المراد البحث فيه

        Returns:
            list: قائمة بكتل الكود
        """
        return TextUtils.CODE_BLOCK_PATTERN.findall(text)

    @staticmethod
    def remove_code_blocks(text: str) -> str:
        """
        إزالة كتل الكود من النص
        Remove code blocks from text.

        Args:
            text: النص المراد معالجته

        Returns:
            str: النص بدون كتل الكود
        """
        return TextUtils.CODE_BLOCK_PATTERN.sub('', text)

    @staticmethod
    def extract_inline_code(text: str) -> List[str]:
        """
        استخراج الكود المضمن من النص
        Extract inline code from text.

        Args:
            text: النص المراد البحث فيه

        Returns:
            list: قائمة بقطع الكود المضمنة
        """
        return TextUtils.INLINE_CODE_PATTERN.findall(text)

    @staticmethod
    def extract_links(text: str) -> List[Tuple[str, str]]:
        """
        استخراج الروابط من النص
        Extract links from text.

        Args:
            text: النص المراد البحث فيه

        Returns:
            list: قائمة بالروابط (النص، الرابط)
        """
        return TextUtils.MARKDOWN_LINK_PATTERN.findall(text)

    @staticmethod
    def preserve_markdown_formatting(text: str) -> Dict[str, List]:
        """
        حفظ عناصر Markdown أثناء المعالجة
        Preserve markdown formatting elements.

        Args:
            text: النص المراد حفظ تنسيقه

        Returns:
            dict: قاموس يحتوي على عناصر Markdown
        """
        return {
            'code_blocks': TextUtils.extract_code_blocks(text),
            'inline_code': TextUtils.extract_inline_code(text),
            'links': TextUtils.extract_links(text),
            'headers': TextUtils._extract_headers(text),
            'lists': TextUtils._extract_lists(text),
        }

    @staticmethod
    def _extract_headers(text: str) -> List[str]:
        """
        استخراج رؤوس Markdown
        Extract markdown headers.

        Args:
            text: النص المراد البحث فيه

        Returns:
            list: قائمة بالرؤوس
        """
        return re.findall(r'^#{1,6}\s+.*$', text, re.MULTILINE)

    @staticmethod
    def _extract_lists(text: str) -> List[str]:
        """
        استخراج عناصر القوائم
        Extract list items.

        Args:
            text: النص المراد البحث فيه

        Returns:
            list: قائمة بعناصر القوائم
        """
        return re.findall(r'^[\s]*[-*+]\s+.*$', text, re.MULTILINE)

    @staticmethod
    def count_arabic_chars(text: str) -> int:
        """
        عد الأحرف العربية في النص
        Count Arabic characters in text.

        Args:
            text: النص المراد العد

        Returns:
            int: عدد الأحرف العربية
        """
        return sum(len(match) for match in TextUtils.ARABIC_PATTERN.findall(text))

    @staticmethod
    def count_english_chars(text: str) -> int:
        """
        عد الأحرف الإنجليزية في النص
        Count English characters in text.

        Args:
            text: النص المراد العد

        Returns:
            int: عدد الأحرف الإنجليزية
        """
        return sum(len(match) for match in TextUtils.ENGLISH_PATTERN.findall(text))

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """
        إزالة المسافات الزائدة
        Remove extra whitespace.

        Args:
            text: النص المراد معالجته

        Returns:
            str: النص بدون مسافات زائدة
        """
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        تطبيع النص
        Normalize text.

        Args:
            text: النص المراد تطبيعه

        Returns:
            str: النص المطبع
        """
        # Remove zero-width spaces and other invisible characters
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        # Normalize Arabic diacritics
        text = re.sub(r'[\u064B-\u065F]', '', text)
        return text

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        تقسيم النص إلى جمل
        Split text into sentences.

        Args:
            text: النص المراد تقسيمه

        Returns:
            list: قائمة بالجمل
        """
        # Split on periods, question marks, exclamation marks
        sentences = re.split(r'([.!?]+)', text)
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if sentences[i].strip():
                result.append(sentences[i] + sentences[i + 1])
        if sentences[-1].strip():
            result.append(sentences[-1])
        return [s.strip() for s in result if s.strip()]

    @staticmethod
    def detect_language(text: str) -> str:
        """
        الكشف عن لغة النص
        Detect text language.

        Args:
            text: النص المراد الكشف عن لغته

        Returns:
            str: "ar" للعربية، "en" للإنجليزية، "mixed" للمخلوط
        """
        arabic_count = TextUtils.count_arabic_chars(text)
        english_count = TextUtils.count_english_chars(text)

        if arabic_count > english_count:
            return "ar"
        elif english_count > arabic_count:
            return "en"
        else:
            return "mixed"

    @staticmethod
    def contains_code_language_markers(text: str) -> List[str]:
        """
        الكشف عن علامات لغات البرمجة
        Detect programming language markers.

        Args:
            text: النص المراد الكشف فيه

        Returns:
            list: قائمة بلغات البرمجة المكتشفة
        """
        languages = []
        patterns = {
            'python': r'def\s+\w+|import\s+\w+|class\s+\w+',
            'javascript': r'function\s+\w+|const\s+\w+|var\s+\w+',
            'typescript': r'interface\s+\w+|type\s+\w+|enum\s+\w+',
            'jsx': r'<[A-Z]\w+|useState|useEffect',
            'fastapi': r'@app\.|FastAPI|from fastapi',
            'react': r'import.*from.*react|useState|useEffect',
        }

        for lang, pattern in patterns.items():
            if re.search(pattern, text):
                languages.append(lang)

        return languages

    @staticmethod
    def get_text_metrics(text: str) -> Dict[str, int]:
        """
        الحصول على مقاييس النص
        Get text metrics.

        Args:
            text: النص المراد تحليله

        Returns:
            dict: قاموس بمقاييس النص
        """
        return {
            'total_chars': len(text),
            'total_words': len(text.split()),
            'arabic_chars': TextUtils.count_arabic_chars(text),
            'english_chars': TextUtils.count_english_chars(text),
            'lines': len(text.split('\n')),
            'code_blocks': len(TextUtils.extract_code_blocks(text)),
            'inline_code': len(TextUtils.extract_inline_code(text)),
            'links': len(TextUtils.extract_links(text)),
        }
