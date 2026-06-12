"""
اختبارات خط الأنابيب
End-to-end pipeline tests (offline, provider="none").
"""

import pytest

from arabic_translator import BatchTranslator, DocumentTranslator

SAMPLE_MD = """---
title: Getting Started
sidebar: 3
---

# Getting Started

The useState hook adds state to components.

```python
print("hello")  # keep me
```

- first item
- second item

1. ordered one
2. ordered two

> A quote line

| Col A | Col B |
|-------|-------|
| 1     | 2     |

Check the [docs](https://example.com/docs?a=1,2) for more.
"""


@pytest.fixture
def translator():
    return DocumentTranslator(provider="none")


def _roundtrip(translator, tmp_path, content, name="doc.md"):
    src = tmp_path / name
    src.write_text(content, encoding="utf-8")
    out = tmp_path / f"out_{name}"
    result = translator.translate_file(str(src), str(out))
    return result, out.read_text(encoding="utf-8")


class TestDocumentTranslator:
    def test_dry_run_flag_reported(self, translator, tmp_path):
        result, _ = _roundtrip(translator, tmp_path, "# Title\n\nBody text.\n")
        assert result["dry_run"] is True
        assert result["status"] == "success"

    def test_structure_preserved(self, translator, tmp_path):
        _, output = _roundtrip(translator, tmp_path, SAMPLE_MD)
        assert "# " in output                       # header marker
        assert "```python" in output                # fence language kept
        assert 'print("hello")  # keep me' in output  # code untouched
        assert "- " in output                       # unordered list
        assert "1. " in output                      # ordered list
        assert "> " in output                       # blockquote
        assert "| Col A | Col B |" in output        # table untouched
        assert "(https://example.com/docs?a=1,2)" in output  # link target intact

    def test_frontmatter_untouched(self, translator, tmp_path):
        _, output = _roundtrip(translator, tmp_path, SAMPLE_MD)
        assert output.startswith("---\ntitle: Getting Started\nsidebar: 3\n---\n\n")

    def test_dry_run_output_is_clean_roundtrip(self, translator, tmp_path):
        """Dry-run output must contain the source text only - no prompt text."""
        _, output = _roundtrip(translator, tmp_path, SAMPLE_MD)
        assert "ترجم النص" not in output
        assert "المصطلحات المعتمدة" not in output
        assert "The useState hook adds state to components." in output

    def test_translation_time_measured(self, translator, tmp_path):
        result, _ = _roundtrip(translator, tmp_path, SAMPLE_MD)
        assert result["translation_time"] >= 0

    def test_mdx_components_survive(self, translator, tmp_path):
        mdx = (
            "import {Tab} from '@theme';\n\n"
            "# Title\n\n"
            "<Tab label=\"one\">content</Tab>\n\n"
            "Plain paragraph.\n"
        )
        _, output = _roundtrip(translator, tmp_path, mdx, name="page.mdx")
        assert "import {Tab} from '@theme';" in output
        assert '<Tab label="one">content</Tab>' in output

    def test_review_pipeline_runs(self, translator, tmp_path):
        src = tmp_path / "doc.md"
        src.write_text("# Title\n\nUse `npm` to install.\n", encoding="utf-8")
        out = tmp_path / "doc_ar.md"
        result = translator.translate_with_review(str(src), str(out))
        assert "review" in result
        assert "approved" in result


class TestBatchTranslator:
    def test_folder_translation_and_summary(self, tmp_path):
        src_dir = tmp_path / "docs"
        src_dir.mkdir()
        (src_dir / "a.md").write_text("# A\n\nFirst file.\n", encoding="utf-8")
        (src_dir / "b.md").write_text("# B\n\nSecond file.\n", encoding="utf-8")
        sub = src_dir / "sub"
        sub.mkdir()
        (sub / "c.md").write_text("# C\n\nThird file.\n", encoding="utf-8")

        batch = BatchTranslator(provider="none", num_workers=2)
        results = batch.translate_folder(str(src_dir), str(tmp_path / "out"))

        assert len(results) == 3
        summary = batch.get_batch_summary(results)
        assert summary["total_files"] == 3
        assert summary["successful"] == 3
        assert (tmp_path / "out" / "sub" / "c.md").exists()

    def test_output_inside_input_not_retranslated(self, tmp_path):
        src_dir = tmp_path / "docs"
        src_dir.mkdir()
        (src_dir / "a.md").write_text("# A\n\nFile.\n", encoding="utf-8")

        out_dir = src_dir / "translated"
        batch = BatchTranslator(provider="none", num_workers=1)

        # First run creates output inside the input folder
        batch.translate_folder(str(src_dir), str(out_dir))
        # Second run must skip files under the output folder
        results = batch.translate_folder(str(src_dir), str(out_dir))
        assert all(not key.startswith("translated") for key in results)
