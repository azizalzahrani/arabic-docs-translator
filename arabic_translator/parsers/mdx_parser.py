"""
محلل MDX
MDX Parser.

يحلل ملفات MDX (Markdown + JSX) مع الحفاظ على مكونات React
Parses MDX files while preserving React components.
"""

import re
from typing import Dict, List, Tuple
from .markdown_parser import MarkdownParser, MarkdownElement


class MDXParser:
    """
    فئة محلل MDX
    MDX parser class.

    تحلل ملفات MDX وتحمي مكونات React والمنطق من الترجمة
    Parses MDX files while protecting React components and logic.
    """

    JSX_COMPONENT_PATTERN = re.compile(
        r'<[A-Z]\w*[^>]*>.*?</[A-Z]\w*>',
        re.DOTALL
    )
    JSX_SELF_CLOSING_PATTERN = re.compile(
        r'<[A-Z]\w*[^>]*/>'
    )
    IMPORT_STATEMENT_PATTERN = re.compile(
        r'^import\s+.+from\s+.+$',
        re.MULTILINE
    )
    EXPORT_STATEMENT_PATTERN = re.compile(
        r'^export\s+.+$',
        re.MULTILINE
    )

    def __init__(self):
        """تهيئة محلل MDX"""
        self.markdown_parser = MarkdownParser()
        self.placeholders: Dict[str, str] = {}
        self.placeholder_counter = 0

    def parse(self, content: str) -> Tuple[List[MarkdownElement], Dict[str, str]]:
        """
        تحليل محتوى MDX
        Parse MDX content.

        Args:
            content: محتوى MDX

        Returns:
            tuple: (عناصر Markdown، قاموس المكونات المحمية)
        """
        # Extract and protect JSX components
        protected_content, jsx_components = self._protect_jsx(content)

        # Extract and protect imports/exports
        protected_content, imports_exports = self._protect_imports_exports(protected_content)

        # Parse remaining markdown
        elements = self.markdown_parser.parse(protected_content)

        # Store all protected elements
        self.placeholders = {**jsx_components, **imports_exports}

        return elements, self.placeholders

    def _protect_jsx(self, content: str) -> Tuple[str, Dict[str, str]]:
        """حماية مكونات JSX"""
        components = {}

        # Protect multi-line components
        def replace_component(match):
            placeholder = self._create_placeholder()
            components[placeholder] = match.group(0)
            return placeholder

        # Process self-closing components first
        content = self.JSX_SELF_CLOSING_PATTERN.sub(replace_component, content)

        # Process multi-line components
        content = self.JSX_COMPONENT_PATTERN.sub(replace_component, content)

        return content, components

    def _protect_imports_exports(self, content: str) -> Tuple[str, Dict[str, str]]:
        """حماية جمل الاستيراد والتصدير"""
        imports = {}

        def replace_import(match):
            placeholder = self._create_placeholder()
            imports[placeholder] = match.group(0)
            return f'{placeholder}\n'

        content = self.IMPORT_STATEMENT_PATTERN.sub(replace_import, content)
        content = self.EXPORT_STATEMENT_PATTERN.sub(replace_import, content)

        return content, imports

    def restore(self, content: str) -> str:
        """
        استعادة جميع المكونات المحمية
        Restore all protected components.

        Args:
            content: المحتوى المعدل

        Returns:
            str: المحتوى مع المكونات المستعادة
        """
        for placeholder, original in self.placeholders.items():
            content = content.replace(placeholder, original)

        return content

    def extract_translatable_content(self, content: str) -> List[str]:
        """
        استخراج المحتوى القابل للترجمة فقط
        Extract only translatable content.

        Args:
            content: محتوى MDX

        Returns:
            list: قائمة بنصوص قابلة للترجمة
        """
        elements, _ = self.parse(content)
        translatable = []

        for element in elements:
            if element.type in ['header', 'paragraph', 'blockquote']:
                translatable.append(element.content)
            elif element.type == 'list':
                items = re.findall(r'[-*+]\s+(.+)', element.content)
                translatable.extend(items)

        return translatable

    def get_mdx_statistics(self, content: str) -> Dict:
        """
        الحصول على إحصائيات MDX
        Get MDX statistics.

        Args:
            content: محتوى MDX

        Returns:
            dict: إحصائيات المحتوى
        """
        elements, protected = self.parse(content)

        return {
            'total_elements': len(elements),
            'jsx_components': len([v for k, v in protected.items() if v.startswith('<')]),
            'imports': len([v for k, v in protected.items() if v.startswith('import')]),
            'exports': len([v for k, v in protected.items() if v.startswith('export')]),
            'headers': len([e for e in elements if e.type == 'header']),
            'paragraphs': len([e for e in elements if e.type == 'paragraph']),
            'code_blocks': len([e for e in elements if e.type == 'code']),
        }

    def validate_mdx(self, content: str) -> Dict[str, any]:
        """
        التحقق من صحة MDX
        Validate MDX content.

        Args:
            content: محتوى MDX

        Returns:
            dict: نتائج التحقق
        """
        issues = []

        # Check for balanced JSX tags
        opening_tags = len(re.findall(r'<[A-Z]\w+[^/]*>', content))
        closing_tags = len(re.findall(r'</[A-Z]\w+>', content))
        self_closing = len(re.findall(r'<[A-Z]\w+[^>]*/>', content))

        if opening_tags != closing_tags + self_closing:
            issues.append('Unbalanced JSX tags detected')

        # Check for unclosed markdown code blocks
        code_block_count = len(re.findall(r'```', content))
        if code_block_count % 2 != 0:
            issues.append('Unclosed markdown code blocks detected')

        # Check for invalid imports
        invalid_imports = re.findall(
            r'import\s+.*from\s+(?![\'\"]).*(?![\'\"])$',
            content,
            re.MULTILINE
        )
        if invalid_imports:
            issues.append(f'Found {len(invalid_imports)} potentially invalid imports')

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'stats': self.get_mdx_statistics(content),
        }

    def _create_placeholder(self) -> str:
        """إنشاء عنصر نائب فريد"""
        self.placeholder_counter += 1
        return f'__MDX_PLACEHOLDER_{self.placeholder_counter}__'

    def extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """
        استخراج frontmatter من MDX
        Extract frontmatter from MDX.

        Args:
            content: محتوى MDX

        Returns:
            tuple: (بيانات Frontmatter، المحتوى المتبقي)
        """
        # Check for YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if yaml_match:
            frontmatter_str = yaml_match.group(1)
            remaining_content = yaml_match.group(2)

            # Parse YAML (simple key-value parsing)
            frontmatter = {}
            for line in frontmatter_str.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"\'')

            return frontmatter, remaining_content

        return {}, content
