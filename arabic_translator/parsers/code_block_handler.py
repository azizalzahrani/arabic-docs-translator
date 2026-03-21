"""
معالج كتل الكود
Code Block Handler.

يستخرج ويحمي كتل الكود من الترجمة
Extracts and protects code blocks from translation.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CodeBlock:
    """تمثيل كتلة كود"""
    code: str
    language: str
    line_start: int
    line_end: int
    placeholder: str = ""


class CodeBlockHandler:
    """
    فئة معالج كتل الكود
    Code block handler class.

    تستخرج الأكواس من المحتوى وتحميها من الترجمة
    Extracts and protects code blocks from translation.
    """

    CODE_BLOCK_PATTERN = re.compile(
        r'```([\w]*)\n(.*?)\n```',
        re.DOTALL | re.IGNORECASE
    )
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')

    def __init__(self):
        """تهيئة معالج الكود"""
        self.code_blocks: Dict[str, CodeBlock] = {}
        self.placeholder_counter = 0

    def extract_code_blocks(self, content: str) -> Tuple[str, Dict[str, CodeBlock]]:
        """
        استخراج كتل الكود من المحتوى
        Extract code blocks from content.

        Args:
            content: المحتوى الذي يحتوي على الأكواس

        Returns:
            tuple: (المحتوى بدون الأكواس، قاموس الأكواس المستخرجة)
        """
        self.code_blocks = {}
        self.placeholder_counter = 0

        def replace_code_block(match):
            language = match.group(1) or 'plaintext'
            code = match.group(2)
            placeholder = self._create_placeholder()

            self.code_blocks[placeholder] = CodeBlock(
                code=code,
                language=language,
                line_start=0,
                line_end=0,
                placeholder=placeholder
            )

            return f'```{language}\n{placeholder}\n```'

        modified_content = self.CODE_BLOCK_PATTERN.sub(replace_code_block, content)
        return modified_content, self.code_blocks

    def extract_inline_code(self, content: str) -> Tuple[str, Dict[str, str]]:
        """
        استخراج الكود المضمن
        Extract inline code.

        Args:
            content: المحتوى

        Returns:
            tuple: (المحتوى المعدل، قاموس الكود المضمن)
        """
        inline_codes = {}

        def replace_inline(match):
            code = match.group(1)
            placeholder = self._create_placeholder()
            inline_codes[placeholder] = code
            return f'`{placeholder}`'

        modified_content = self.INLINE_CODE_PATTERN.sub(replace_inline, content)
        return modified_content, inline_codes

    def translate_comments_in_code(
        self,
        code: str,
        language: str,
        translator_func
    ) -> str:
        """
        ترجمة التعليقات في الكود فقط
        Translate comments in code only.

        Args:
            code: كود البرنامج
            language: لغة البرمجة
            translator_func: دالة الترجمة

        Returns:
            str: الكود مع التعليقات المترجمة
        """
        if language.lower() in ['python', 'py']:
            return self._translate_python_comments(code, translator_func)
        elif language.lower() in ['javascript', 'js', 'jsx', 'typescript', 'ts', 'tsx']:
            return self._translate_js_comments(code, translator_func)
        elif language.lower() in ['java', 'cpp', 'c', 'csharp', 'cs']:
            return self._translate_c_style_comments(code, translator_func)
        else:
            # For unknown languages, try to find common comment patterns
            return self._translate_generic_comments(code, translator_func)

    def _translate_python_comments(self, code: str, translator_func) -> str:
        """ترجمة التعليقات في Python"""
        lines = code.split('\n')
        result = []

        for line in lines:
            # Find comment in line
            comment_match = re.search(r'#(.*)$', line)
            if comment_match:
                before_comment = line[:comment_match.start()]
                comment_text = comment_match.group(1).strip()

                # Only translate non-empty comments
                if comment_text and not comment_text.startswith('noqa'):
                    translated_comment = translator_func(comment_text)
                    line = f'{before_comment}# {translated_comment}'

            result.append(line)

        return '\n'.join(result)

    def _translate_js_comments(self, code: str, translator_func) -> str:
        """ترجمة التعليقات في JavaScript/TypeScript"""
        # Handle single-line comments
        code = re.sub(
            r'//\s*(.+?)$',
            lambda m: f'// {translator_func(m.group(1))}',
            code,
            flags=re.MULTILINE
        )

        # Handle multi-line comments
        code = re.sub(
            r'/\*\s*(.*?)\s*\*/',
            lambda m: f'/* {translator_func(m.group(1))} */',
            code,
            flags=re.DOTALL
        )

        return code

    def _translate_c_style_comments(self, code: str, translator_func) -> str:
        """ترجمة التعليقات في لغات C-style"""
        # Handle single-line comments
        code = re.sub(
            r'//\s*(.+?)$',
            lambda m: f'// {translator_func(m.group(1))}',
            code,
            flags=re.MULTILINE
        )

        # Handle multi-line comments
        code = re.sub(
            r'/\*\s*(.*?)\s*\*/',
            lambda m: f'/* {translator_func(m.group(1))} */',
            code,
            flags=re.DOTALL
        )

        return code

    def _translate_generic_comments(self, code: str, translator_func) -> str:
        """ترجمة التعليقات في اللغات المجهولة"""
        # Handle common comment patterns
        lines = code.split('\n')
        result = []

        for line in lines:
            # Python-style comments
            if '#' in line and not line.strip().startswith('#!'):
                parts = line.split('#', 1)
                comment = parts[1].strip()
                if comment:
                    translated = translator_func(comment)
                    line = f'{parts[0]}# {translated}'

            result.append(line)

        return '\n'.join(result)

    def restore_code_blocks(
        self,
        content: str,
        code_blocks: Dict[str, CodeBlock]
    ) -> str:
        """
        استعادة كتل الكود الأصلية
        Restore original code blocks.

        Args:
            content: المحتوى المعدل
            code_blocks: قاموس الأكواس الأصلية

        Returns:
            str: المحتوى مع الأكواس المستعادة
        """
        for placeholder, code_block in code_blocks.items():
            content = content.replace(placeholder, code_block.code)

        return content

    def restore_inline_code(self, content: str, inline_codes: Dict[str, str]) -> str:
        """
        استعادة الكود المضمن الأصلي
        Restore original inline code.

        Args:
            content: المحتوى المعدل
            inline_codes: قاموس الأكواس المضمنة

        Returns:
            str: المحتوى مع الأكواس المستعادة
        """
        for placeholder, code in inline_codes.items():
            content = content.replace(placeholder, code)

        return content

    def detect_code_language(self, code: str) -> str:
        """
        الكشف عن لغة البرمجة
        Detect programming language.

        Args:
            code: كود البرنامج

        Returns:
            str: اسم اللغة
        """
        # Check for JSX before plain JavaScript so mixed snippets classify correctly.
        jsx_pattern = re.search(
            r'<[A-Za-z][\w:-]*\b[^>]*>|useState|useEffect|=>\s*<',
            code
        )
        if jsx_pattern:
            return 'jsx'

        # Check for Python
        if re.search(r'\bdef\s+\w+|import\s+\w+|class\s+\w+', code):
            return 'python'

        # Check for JavaScript/TypeScript
        if re.search(r'\bfunction\s+\w+|const\s+\w+|let\s+\w+|var\s+\w+', code):
            return 'javascript'

        # Check for Java
        if re.search(r'\bpublic\s+class\s+\w+|import\s+java', code):
            return 'java'

        # Check for C/C++
        if re.search(r'#include|int\s+main|printf', code):
            return 'cpp'

        # Check for FastAPI
        if re.search(r'from fastapi|@app\.|FastAPI', code):
            return 'python'

        return 'plaintext'

    def _create_placeholder(self) -> str:
        """إنشاء عنصر نائب فريد"""
        self.placeholder_counter += 1
        return f'__CODE_BLOCK_{self.placeholder_counter}__'

    def get_code_statistics(self, content: str) -> Dict:
        """
        الحصول على إحصائيات الكود
        Get code statistics.

        Args:
            content: المحتوى

        Returns:
            dict: إحصائيات الكود
        """
        code_blocks = self.CODE_BLOCK_PATTERN.findall(content)
        languages = {}

        for language, code in code_blocks:
            lang = language or 'plaintext'
            if lang not in languages:
                languages[lang] = {'count': 0, 'total_lines': 0}
            languages[lang]['count'] += 1
            languages[lang]['total_lines'] += len(code.split('\n'))

        return {
            'total_code_blocks': len(code_blocks),
            'languages': languages,
            'inline_code_snippets': len(self.INLINE_CODE_PATTERN.findall(content)),
        }
