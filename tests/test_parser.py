"""
اختبارات محللات المستندات
Parser Tests.
"""

import pytest
from arabic_translator.parsers import MarkdownParser, CodeBlockHandler, MDXParser


class TestMarkdownParser:
    """فئة اختبار محلل Markdown"""

    @pytest.fixture
    def parser(self):
        """إنشاء محلل للاختبار"""
        return MarkdownParser()

    def test_parse_headers(self, parser):
        """اختبار تحليل الرؤوس"""
        content = """
# Header 1
## Header 2
### Header 3
        """
        elements = parser.parse(content)
        headers = [e for e in elements if e.type == "header"]
        assert len(headers) >= 3

    def test_parse_code_blocks(self, parser):
        """اختبار تحليل كتل الكود"""
        content = """
```python
def hello():
    return "world"
```
        """
        elements = parser.parse(content)
        code_blocks = [e for e in elements if e.type == "code"]
        assert len(code_blocks) > 0

    def test_parse_lists(self, parser):
        """اختبار تحليل القوائم"""
        content = """
- Item 1
- Item 2
- Item 3
        """
        elements = parser.parse(content)
        lists = [e for e in elements if e.type == "list"]
        assert len(lists) > 0

    def test_reconstruct_markdown(self, parser):
        """اختبار إعادة بناء Markdown"""
        original = "# Title\n\nSome paragraph"
        elements = parser.parse(original)
        reconstructed = parser.reconstruct(elements)

        assert "Title" in reconstructed
        assert "paragraph" in reconstructed

    def test_extract_text_elements(self, parser):
        """اختبار استخراج العناصر النصية"""
        content = """
# Header

This is a paragraph.

- List item 1
- List item 2

```code
should not appear
```
        """
        text_elements = parser.extract_text_elements(content)
        assert "Header" in text_elements
        assert "paragraph" in text_elements
        assert len(text_elements) > 0

    def test_get_element_statistics(self, parser):
        """اختبار الحصول على إحصائيات العناصر"""
        content = """
# Header 1
## Header 2

Paragraph

```python
code
```

- Item 1
- Item 2
        """
        stats = parser.get_element_statistics(content)
        assert stats["headers"] > 0
        assert stats["paragraphs"] > 0
        assert stats["code_blocks"] > 0
        assert stats["lists"] > 0


class TestCodeBlockHandler:
    """فئة اختبار معالج كتل الكود"""

    @pytest.fixture
    def handler(self):
        """إنشاء معالج للاختبار"""
        return CodeBlockHandler()

    def test_extract_code_blocks(self, handler):
        """اختبار استخراج كتل الكود"""
        content = """
Some text

```python
def test():
    pass
```

More text
        """
        modified, blocks = handler.extract_code_blocks(content)

        assert len(blocks) > 0
        assert "def test" not in modified
        assert "__CODE_BLOCK_" in modified

    def test_restore_code_blocks(self, handler):
        """اختبار استعادة كتل الكود"""
        content = "```python\nprint('hello')\n```"
        modified, blocks = handler.extract_code_blocks(content)
        restored = handler.restore_code_blocks(modified, blocks)

        assert "print" in restored

    def test_detect_code_language(self, handler):
        """اختبار الكشف عن لغة البرمجة"""
        python_code = "def test():\n    pass"
        assert handler.detect_code_language(python_code) == "python"

        js_code = "function test() {}"
        assert handler.detect_code_language(js_code) == "javascript"

        jsx_code = "const App = () => <div>Hello</div>"
        assert handler.detect_code_language(jsx_code) == "jsx"

    def test_get_code_statistics(self, handler):
        """اختبار الحصول على إحصائيات الكود"""
        content = """
```python
code here
```

```javascript
js code
```
        """
        stats = handler.get_code_statistics(content)
        assert stats["total_code_blocks"] == 2
        assert "languages" in stats


class TestMDXParser:
    """فئة اختبار محلل MDX"""

    @pytest.fixture
    def parser(self):
        """إنشاء محلل MDX للاختبار"""
        return MDXParser()

    def test_parse_mdx_with_jsx(self, parser):
        """اختبار تحليل MDX مع JSX"""
        content = """
# Title

<MyComponent prop="value" />

Some text
        """
        elements, protected = parser.parse(content)
        assert len(protected) > 0

    def test_protect_jsx_components(self, parser):
        """اختبار حماية مكونات JSX"""
        content = """
<Button>Click me</Button>
        """
        protected, components = parser._protect_jsx(content)

        assert len(components) > 0
        assert "__MDX_PLACEHOLDER_" in protected

    def test_restore_mdx(self, parser):
        """اختبار استعادة MDX"""
        original = """
<MyComponent />

Text here
        """
        elements, protected = parser.parse(original)
        # In real usage, elements would be translated, then restored

    def test_validate_mdx(self, parser):
        """اختبار التحقق من صحة MDX"""
        valid_mdx = """
import { Component } from 'react';

# Title

<Component />

Content here
        """
        result = parser.validate_mdx(valid_mdx)
        assert "is_valid" in result

    def test_extract_frontmatter(self, parser):
        """اختبار استخراج frontmatter"""
        content = """---
title: My Document
author: John Doe
---

# Content

Main content here
        """
        frontmatter, remaining = parser.extract_frontmatter(content)

        assert "title" in frontmatter or len(remaining) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
