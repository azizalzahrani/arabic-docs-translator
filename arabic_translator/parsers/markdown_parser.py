"""
محلل Markdown
Markdown Parser.

يحلل ملفات Markdown ويحافظ على تنسيقها
Parses markdown files while preserving formatting.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MarkdownElement:
    """
    عنصر Markdown
    Markdown element representation.
    """
    type: str  # 'header', 'paragraph', 'code', 'list', 'table', 'link', 'image'
    content: str
    level: Optional[int] = None  # For headers
    metadata: Dict = None


class MarkdownParser:
    """
    فئة محلل Markdown
    Markdown parser class.

    تحلل ملفات Markdown وتحافظ على التنسيق الكامل
    Parses markdown files while preserving complete formatting.
    """

    # Patterns for markdown elements
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    BOLD_PATTERN = re.compile(r'\*\*(.+?)\*\*')
    ITALIC_PATTERN = re.compile(r'\*(.+?)\*')
    CODE_BLOCK_PATTERN = re.compile(
        r'```(?:[\w]+)?\n(.*?)\n```',
        re.DOTALL
    )
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
    UNORDERED_LIST_PATTERN = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE)
    TABLE_PATTERN = re.compile(r'^\|(.+)\|$', re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s+(.+)$', re.MULTILINE)
    HORIZONTAL_RULE_PATTERN = re.compile(r'^(---|\*\*\*|___)$', re.MULTILINE)

    def __init__(self):
        """تهيئة محلل Markdown"""
        pass

    def parse(self, content: str) -> List[MarkdownElement]:
        """
        تحليل محتوى Markdown
        Parse markdown content.

        Args:
            content: محتوى Markdown

        Returns:
            list: قائمة بعناصر Markdown
        """
        elements = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for headers
            header_match = self.HEADER_PATTERN.match(line)
            if header_match:
                level = len(header_match.group(1))
                content_text = header_match.group(2)
                elements.append(MarkdownElement(
                    type='header',
                    content=content_text,
                    level=level
                ))
                i += 1
                continue

            # Check for code blocks
            if line.strip().startswith('```'):
                code_block, end_idx = self._extract_code_block(lines, i)
                elements.append(MarkdownElement(
                    type='code',
                    content=code_block
                ))
                i = end_idx + 1
                continue

            # Check for tables
            if line.strip().startswith('|'):
                table, end_idx = self._extract_table(lines, i)
                elements.append(MarkdownElement(
                    type='table',
                    content=table
                ))
                i = end_idx + 1
                continue

            # Check for blockquotes
            if line.strip().startswith('>'):
                blockquote, end_idx = self._extract_blockquote(lines, i)
                elements.append(MarkdownElement(
                    type='blockquote',
                    content=blockquote
                ))
                i = end_idx + 1
                continue

            # Check for lists
            if re.match(r'^[\s]*[-*+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
                list_items, end_idx = self._extract_list(lines, i)
                elements.append(MarkdownElement(
                    type='list',
                    content=list_items
                ))
                i = end_idx + 1
                continue

            # Check for horizontal rules
            if re.match(r'^(---|\*\*\*|___)$', line.strip()):
                elements.append(MarkdownElement(
                    type='horizontal_rule',
                    content=line
                ))
                i += 1
                continue

            # Regular paragraph
            if line.strip():
                paragraph, end_idx = self._extract_paragraph(lines, i)
                elements.append(MarkdownElement(
                    type='paragraph',
                    content=paragraph
                ))
                i = end_idx + 1
            else:
                i += 1

        return elements

    def _extract_code_block(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """استخراج كتلة كود"""
        content = []
        i = start_idx + 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            content.append(lines[i])
            i += 1
        return '\n'.join(content), i

    def _extract_table(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """استخراج جدول"""
        content = [lines[start_idx]]
        i = start_idx + 1
        while i < len(lines) and lines[i].strip().startswith('|'):
            content.append(lines[i])
            i += 1
        return '\n'.join(content), i - 1

    def _extract_blockquote(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """استخراج اقتباس"""
        content = []
        i = start_idx
        while i < len(lines) and lines[i].strip().startswith('>'):
            content.append(lines[i])
            i += 1
        return '\n'.join(content), i - 1

    def _extract_list(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """استخراج قائمة"""
        content = []
        i = start_idx
        base_indent = len(lines[i]) - len(lines[i].lstrip())

        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if re.match(r'^[\s]*[-*+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
                content.append(line)
                i += 1
            else:
                break

        return '\n'.join(content), i - 1 if content else start_idx

    def _extract_paragraph(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """استخراج فقرة"""
        content = [lines[start_idx]]
        i = start_idx + 1

        while i < len(lines):
            line = lines[i]
            if not line.strip():
                break
            if any([
                line.strip().startswith('#'),
                line.strip().startswith('```'),
                line.strip().startswith('|'),
                line.strip().startswith('>'),
                re.match(r'^[\s]*[-*+]\s+', line),
                re.match(r'^[\s]*\d+\.\s+', line),
            ]):
                break
            content.append(line)
            i += 1

        return '\n'.join(content), i - 1

    def reconstruct(self, elements: List[MarkdownElement]) -> str:
        """
        إعادة بناء محتوى Markdown من العناصر
        Reconstruct markdown content from elements.

        Args:
            elements: قائمة عناصر Markdown

        Returns:
            str: محتوى Markdown المعاد بناؤه
        """
        result = []

        for element in elements:
            if element.type == 'header':
                prefix = '#' * element.level
                result.append(f'{prefix} {element.content}')
            elif element.type == 'code':
                result.append(f'```\n{element.content}\n```')
            elif element.type == 'paragraph':
                result.append(element.content)
            elif element.type == 'list':
                result.append(element.content)
            elif element.type == 'table':
                result.append(element.content)
            elif element.type == 'blockquote':
                result.append(element.content)
            elif element.type == 'horizontal_rule':
                result.append(element.content)
            else:
                result.append(element.content)

            result.append('')  # Add blank line between elements

        return '\n'.join(result).rstrip()

    def extract_text_elements(self, content: str) -> List[str]:
        """
        استخراج العناصر النصية فقط (للترجمة)
        Extract only text elements for translation.

        Args:
            content: محتوى Markdown

        Returns:
            list: قائمة بالعناصر النصية
        """
        elements = self.parse(content)
        text_elements = []

        for element in elements:
            if element.type in ['header', 'paragraph', 'blockquote']:
                text_elements.append(element.content)
            elif element.type == 'list':
                # Extract individual list items
                items = re.findall(r'[-*+]\s+(.+)', element.content)
                text_elements.extend(items)

        return text_elements

    def get_element_statistics(self, content: str) -> Dict:
        """
        الحصول على إحصائيات العناصر
        Get element statistics.

        Args:
            content: محتوى Markdown

        Returns:
            dict: إحصائيات العناصر
        """
        elements = self.parse(content)
        stats = {
            'total_elements': len(elements),
            'headers': 0,
            'paragraphs': 0,
            'code_blocks': 0,
            'lists': 0,
            'tables': 0,
            'blockquotes': 0,
        }

        for element in elements:
            if element.type in stats:
                stats[element.type + 's'] = stats.get(element.type + 's', 0) + 1

        return stats
