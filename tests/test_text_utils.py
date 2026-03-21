"""
اختبارات أدوات معالجة النصوص
Text Utils Tests.
"""

import pytest
from arabic_translator.utils import TextUtils


class TestTextUtils:
    """فئة اختبار أدوات معالجة النصوص"""

    def test_is_arabic(self):
        """اختبار كشف اللغة العربية"""
        assert TextUtils.is_arabic("مرحبا بك") is True
        assert TextUtils.is_arabic("Hello world") is False
        assert TextUtils.is_arabic("مرحبا Hello") is True

    def test_is_english(self):
        """اختبار كشف اللغة الإنجليزية"""
        assert TextUtils.is_english("Hello world") is True
        assert TextUtils.is_english("مرحبا بك") is False
        assert TextUtils.is_english("Hello مرحبا") is True

    def test_extract_code_blocks(self):
        """اختبار استخراج كتل الكود"""
        text = """
```python
def hello():
    return "world"
```

Some text here

```javascript
console.log('hello');
```
        """
        blocks = TextUtils.extract_code_blocks(text)
        assert len(blocks) == 2

    def test_extract_inline_code(self):
        """اختبار استخراج الكود المضمن"""
        text = "Use the `function` keyword to define a `method`"
        inline = TextUtils.extract_inline_code(text)
        assert len(inline) == 2
        assert "function" in inline
        assert "method" in inline

    def test_extract_links(self):
        """اختبار استخراج الروابط"""
        text = "Check [GitHub](https://github.com) and [Google](https://google.com)"
        links = TextUtils.extract_links(text)
        assert len(links) == 2
        assert links[0][0] == "GitHub"
        assert links[1][0] == "Google"

    def test_count_arabic_chars(self):
        """اختبار عد الأحرف العربية"""
        text = "مرحبا Hello"
        count = TextUtils.count_arabic_chars(text)
        assert count == 5

    def test_count_english_chars(self):
        """اختبار عد الأحرف الإنجليزية"""
        text = "مرحبا Hello"
        count = TextUtils.count_english_chars(text)
        assert count == 5

    def test_remove_extra_whitespace(self):
        """اختبار إزالة المسافات الزائدة"""
        text = "Hello   world    foo"
        clean = TextUtils.remove_extra_whitespace(text)
        assert clean == "Hello world foo"

    def test_detect_language(self):
        """اختبار كشف اللغة"""
        assert TextUtils.detect_language("مرحبا بك في العالم") == "ar"
        assert TextUtils.detect_language("Hello world") == "en"
        assert TextUtils.detect_language("مرحبا Hello") in ["mixed", "ar", "en"]

    def test_split_into_sentences(self):
        """اختبار تقسيم النص إلى جمل"""
        text = "This is sentence one. This is sentence two! And a question?"
        sentences = TextUtils.split_into_sentences(text)
        assert len(sentences) == 3

    def test_preserve_markdown_formatting(self):
        """اختبار حفظ تنسيق Markdown"""
        text = """
# Header
**Bold** and *italic*
[Link](http://example.com)
`code`
- List item
        """
        result = TextUtils.preserve_markdown_formatting(text)
        assert "code_blocks" in result
        assert "links" in result
        assert "headers" in result
        assert "lists" in result

    def test_get_text_metrics(self):
        """اختبار الحصول على مقاييس النص"""
        text = "This is a test. مرحبا بك"
        metrics = TextUtils.get_text_metrics(text)

        assert "total_chars" in metrics
        assert "total_words" in metrics
        assert "arabic_chars" in metrics
        assert "english_chars" in metrics
        assert metrics["arabic_chars"] > 0
        assert metrics["english_chars"] > 0

    def test_normalize_text(self):
        """اختبار تطبيع النص"""
        text = "مرحبا‌بك"  # Contains zero-width space
        normalized = TextUtils.normalize_text(text)
        assert "‌" not in normalized

    def test_contains_code_language_markers(self):
        """اختبار الكشف عن لغات البرمجة"""
        python_code = """
def hello():
    return "world"
        """
        languages = TextUtils.contains_code_language_markers(python_code)
        assert "python" in languages

        js_code = """
const x = 10;
function test() {}
        """
        languages = TextUtils.contains_code_language_markers(js_code)
        assert "javascript" in languages

    def test_remove_code_blocks(self):
        """اختبار إزالة كتل الكود"""
        text = """
Introduction

```python
def hello():
    pass
```

Conclusion
        """
        cleaned = TextUtils.remove_code_blocks(text)
        assert "Introduction" in cleaned
        assert "Conclusion" in cleaned
        assert "def hello" not in cleaned


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
