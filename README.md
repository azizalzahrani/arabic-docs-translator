# Arabic Documentation Translator

Translate technical documentation from English to Arabic while preserving Markdown structure, code blocks, and terminology.

مترجم للتوثيقات التقنية من الإنجليزية إلى العربية مع الحفاظ على تنسيق Markdown وMDX وسلامة الأكواد والمصطلحات.

## Why This Project?

Arabic technical content often loses quality when it is translated as plain text. This project is built around a documentation-aware pipeline that keeps structure intact and treats technical wording more carefully.

It focuses on:

- Markdown and MDX parsing
- Code block protection during translation
- Glossary-driven terminology handling
- Review and adaptation stages
- Batch processing for docs folders
- Quality scoring for generated output
- A simple CLI and Python API

## Project Status

This repository currently provides the pipeline structure, parser layer, glossary system, batch tooling, examples, tests, and a working CLI.

The provider-facing LLM call is still an integration point inside [`arabic_translator/agents/translator_agent.py`](arabic_translator/agents/translator_agent.py), so production-grade live translation requires wiring your preferred provider there.

## Highlights

- Preserves Markdown headers, lists, tables, blockquotes, and links
- Keeps code blocks separate from translatable prose
- Supports `.md` and `.mdx` inputs
- Includes built-in technical glossaries
- Supports custom glossary loading
- Exposes single-file and batch workflows
- Returns quality metadata with translation results

## Installation

```bash
git clone https://github.com/azizalzahrani/arabic-docs-translator.git
cd arabic-docs-translator

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -e .
```

If you only want the raw dependencies without editable install:

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Example values:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai
TRANSLATION_MODEL=gpt-4
REVIEW_MODEL=gpt-4
ADAPTER_MODEL=gpt-4
QUALITY_THRESHOLD=0.8
```

The environment file is mainly useful once you connect a live provider implementation in the agent layer.

## Quick Start

### CLI

Translate a single file:

```bash
arabic-translate docs/readme.md --output docs/readme_ar.md --review
```

Translate a folder:

```bash
arabic-translate docs --batch --pattern "*.md" --output translated_docs
```

You can also run the package as a module:

```bash
python -m arabic_translator --help
```

### Python API

Translate a single Markdown file:

```python
from arabic_translator import DocumentTranslator

translator = DocumentTranslator(
    quality_threshold=0.8,
    model="gpt-4",
)

result = translator.translate_file(
    input_path="docs/getting-started.md",
    output_path="docs/getting-started_ar.md",
)

print(result["status"])
print(result["quality_score"])
print(result["output_path"])
```

Translate and run the review step:

```python
from arabic_translator import DocumentTranslator

translator = DocumentTranslator()

result = translator.translate_with_review(
    input_path="docs/api.md",
    output_path="docs/api_ar.md",
)

print(result["approved"])
print(result["review"])
```

Batch translate a docs folder:

```python
from arabic_translator import BatchTranslator

batch = BatchTranslator(num_workers=4, quality_threshold=0.8)

results = batch.translate_folder(
    input_folder="docs",
    output_folder="docs_ar",
    file_pattern="*.md",
)

summary = batch.get_batch_summary(results)
print(summary)
```

Use a custom glossary:

```python
from pathlib import Path

from arabic_translator import DocumentTranslator, GlossaryManager

Path("glossaries").mkdir(exist_ok=True)

glossary = GlossaryManager()
glossary.add_term("component", "مكوّن")
glossary.add_term("state", "الحالة")
glossary.save_glossary("glossaries/custom.json")

translator = DocumentTranslator(glossary_path="glossaries/custom.json")
```

## What The API Returns

`DocumentTranslator.translate_file(...)` returns a dictionary that includes:

- `status`
- `input_path`
- `output_path`
- `file_type`
- `quality_score`
- `quality_report`
- `quality_passed`
- `translation_time`

`DocumentTranslator.translate_with_review(...)` adds:

- `review`
- `approved`

## Supported Inputs

- `.md` for Markdown documentation
- `.mdx` for MDX documentation
- Other file extensions are treated as plain text fallback

## Example Translation Intent

```text
Original:
"The useState hook allows you to add state to functional components."

Desired Arabic style:
"يتيح لك خُطّاف useState إضافة الحالة (State) إلى المكوّنات الدالية."
```

The goal is not literal machine translation. The goal is Arabic technical writing that still sounds natural to developers.

## Project Layout

```text
arabic_translator/
├── agents/
├── glossary/
├── parsers/
├── utils/
├── cli.py
├── config.py
└── pipeline.py

docs/
examples/
tests/
```

Useful files:

- [`examples/translate_markdown.py`](examples/translate_markdown.py)
- [`examples/batch_translate.py`](examples/batch_translate.py)
- [`examples/custom_glossary.py`](examples/custom_glossary.py)
- [`docs/ARCHITECTURE_AR.md`](docs/ARCHITECTURE_AR.md)

## Arabic Summary

### نبذة سريعة

- الأداة موجّهة لترجمة التوثيقات التقنية للعربية بشكل يحافظ على بنية المستند
- تدعم ملفات Markdown وMDX
- تفصل الأكواد عن النصوص القابلة للترجمة
- تتضمن قاموساً تقنياً مدمجاً وقواميس مخصصة
- تدعم الترجمة الفردية والدفعية
- توفر واجهة استخدام عبر Python وCLI

### ملاحظة مهمة

النسخة الحالية منظّمة بشكل جيد من ناحية البنية، الاختبارات، الواجهة البرمجية، وأدوات المعالجة. لكن ربط موفري الترجمة الفعليين ما زال يحتاج إكمال داخل طبقة الوكلاء إذا كنت تريد استخداماً إنتاجياً حقيقياً.

## Roadmap

- Wire live OpenAI and Anthropic provider integrations
- Expand glossary coverage for more frameworks and domains
- Add documentation-platform integrations
- Improve translation memory and consistency workflows
- Explore a lightweight web interface

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a branch: `git checkout -b feature/my-change`
3. Commit your work: `git commit -m "feat: describe change"`
4. Push your branch: `git push origin feature/my-change`
5. Open a pull request.

## Support

- Issues: https://github.com/azizalzahrani/arabic-docs-translator/issues
- Repository: https://github.com/azizalzahrani/arabic-docs-translator
- Contact: contact@azizalzahrani.dev

## License

MIT. See [`LICENSE`](LICENSE).
