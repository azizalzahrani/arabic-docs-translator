# معمارية مترجم التوثيقات التقنية للعربية
## Architecture of Arabic Documentation Translator

---

## نظرة عامة
هذا المشروع يستخدم معمارية متعددة الوكلاء (Multi-Agent Pipeline) لترجمة التوثيقات التقنية من الإنجليزية إلى العربية بجودة عالية.

## مكونات النظام الأساسية

### 1. طبقة المدخلات (Input Layer)
```
المدخلات
  ↓
معالجات الملفات
  ├── MarkdownParser
  ├── MDXParser
  └── CodeBlockHandler
```

- **MarkdownParser**: يحلل ملفات Markdown ويحافظ على جميع عناصر التنسيق
- **MDXParser**: يتعامل مع ملفات MDX (React docs format)
- **CodeBlockHandler**: يستخرج الأكواس ويحميها من الترجمة

### 2. طبقة معالجة اللغة (Language Processing)
```
النص المراد ترجمته
  ↓
TextUtils
  ├── Language Detection
  ├── Code Block Extraction
  ├── Text Metrics
  └── Normalization
```

### 3. طبقة القاموس (Glossary Layer)
```
GlossaryManager
  ├── tech_glossary.json (50+ term)
  ├── framework_terms.json (React, FastAPI, etc.)
  └── Custom Glossaries
```

**المصطلحات المدمجة:**
- Technical: API, Database, Function, Variable, Array, Object, etc.
- React: component, useState, useEffect, props, state, hook
- FastAPI: endpoint, route, request, response, dependency
- Python: function, class, module, import, exception

### 4. طبقة الوكلاء (Agents Layer)

#### Translator Agent (وكيل الترجمة)
```python
Input: English text
  ↓
- Prepare glossary context
- Create translation prompt
- Call LLM API
- Store in translation history
  ↓
Output: Arabic text
```

**المسؤوليات:**
- ترجمة النصوص من الإنجليزية إلى العربية
- استخدام سياق القاموس التقني
- دعم النطاق والسياق (React, FastAPI, Python)

#### Reviewer Agent (وكيل المراجعة)
```python
Input: Original + Translated text
  ↓
- Check terminology consistency
- Verify technical accuracy
- Detect untranslated terms
- Check markdown preservation
- Check code block integrity
  ↓
Output: Review report + Quality score
```

**المقاييس:**
- Consistency Score: 0.0 - 1.0
- Technical Accuracy: 0.0 - 1.0
- Overall Approval: True/False

#### Adapter Agent (وكيل التكييف)
```python
Input: Translated text
  ↓
- Grammar adaptation
- Terminology polishing
- Punctuation adaptation
- Cultural localization
  ↓
Output: Final translated text
```

### 5. طبقة تقييم الجودة (Quality Scoring)

```
QualityScorer
  ├── Glossary Usage (30%)
  ├── Markdown Preservation (20%)
  ├── Code Safety (20%)
  ├── Text Quality (20%)
  └── Arabic Grammar (10%)
```

**الحد الأدنى للجودة:** 0.8 (قابل للتعديل)

### 6. خط الأنابيب الكامل (Complete Pipeline)

```
Input Document
  ↓
[Parser Selection]
  ├── Markdown Parser
  ├── MDX Parser
  └── Plain Text Handler
  ↓
[Element Extraction]
  ├── Code Blocks
  ├── Inline Code
  ├── Links
  └── Markdown Structure
  ↓
[Translation Phase]
  ├── Glossary Lookup
  ├── LLM Translation
  └── Translation History
  ↓
[Review Phase]
  ├── Terminology Check
  ├── Technical Accuracy
  └── Code Safety Verification
  ↓
[Adaptation Phase]
  ├── Grammar Adaptation
  ├── Localization
  └── Final Polishing
  ↓
[Quality Scoring]
  ├── Score Calculation
  ├── Issue Detection
  └── Recommendations
  ↓
[Reconstruction]
  ├── Element Restoration
  ├── Format Preservation
  └── Code Block Restoration
  ↓
Output Document
```

## تدفق البيانات

### Single Document Translation
```
DocumentTranslator.translate_file()
  ↓
1. Read input file
2. Parse document structure
3. Extract translatable elements
4. For each element:
   - Translator Agent → Arabic text
   - Reviewer Agent → Quality check
   - Adapter Agent → Final polish
5. Reconstruct document
6. Calculate quality score
7. Write output file
```

### Batch Translation
```
BatchTranslator.translate_folder()
  ↓
1. Find all matching files
2. For each file:
   - DocumentTranslator.translate_file()
   - Store results
3. Generate batch summary
4. Report statistics
```

## معايير الجودة

### الاختبارات المجراة

1. **Glossary Usage**: هل يتم استخدام مصطلحات القاموس بشكل صحيح؟
2. **Markdown Preservation**: هل يتم الحفاظ على جميع عناصر Markdown؟
3. **Code Safety**: هل تبقى الأكواس غير مترجمة وسليمة؟
4. **Text Quality**: هل النص المترجم سلس وسهل القراءة؟
5. **Arabic Grammar**: هل القواعد اللغوية العربية صحيحة؟

### النقاط المكتسبة

- ✅ استخدام مصطلح من القاموس: +0.1
- ✅ حفظ عنصر Markdown: +0.15
- ✅ عدم ترجمة كود: +0.2
- ✅ نص عالي الجودة: +0.2
- ✅ قواعد لغوية صحيحة: +0.1

## الملفات والمجلدات

```
arabic-docs-translator/
├── arabic_translator/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── pipeline.py               # Main translation pipeline
│   ├── agents/                   # Translation agents
│   │   ├── translator_agent.py
│   │   ├── reviewer_agent.py
│   │   └── adapter_agent.py
│   ├── parsers/                  # Document parsers
│   │   ├── markdown_parser.py
│   │   ├── code_block_handler.py
│   │   └── mdx_parser.py
│   ├── glossary/                 # Glossary management
│   │   ├── tech_glossary.json
│   │   ├── framework_terms.json
│   │   └── glossary_manager.py
│   └── utils/                    # Utilities
│       ├── text_utils.py
│       └── quality_scorer.py
├── examples/                     # Usage examples
│   ├── translate_markdown.py
│   ├── translate_react_docs.py
│   ├── batch_translate.py
│   └── custom_glossary.py
├── tests/                        # Test suite
│   ├── test_glossary.py
│   ├── test_text_utils.py
│   └── test_parser.py
└── docs/                         # Documentation
    └── ARCHITECTURE_AR.md
```

## الإعدادات والمتغيرات

### Config Variables (من .env)
```
OPENAI_API_KEY=...
TRANSLATION_MODEL=gpt-4
QUALITY_THRESHOLD=0.8
GLOSSARY_STRICT=true
TARGET_LANGUAGE=ar
DIALECT=ar_SA
```

## الأداء والتحسينات المستقبلية

### الحالية
- ترجمة أفردية وجماعية (دفعية)
- دعم Markdown و MDX
- قاموس متعدد المستويات
- تقييم جودة شامل

### المخططة
- 🔄 Support for more languages
- 🌐 Web UI for easy access
- 📡 API server
- 💾 Translation memory (TM)
- 🤝 Real-time collaboration
- 🔌 Plugin system for integrations

## أمثلة الاستخدام

### Basic Translation
```python
translator = DocumentTranslator()
result = translator.translate_file("input.md", "output_ar.md")
```

### With Custom Glossary
```python
translator = DocumentTranslator(glossary_path="my_glossary.json")
result = translator.translate_file("input.md", "output_ar.md")
```

### Batch Processing
```python
batch = BatchTranslator(num_workers=4)
results = batch.translate_folder("./docs", "./docs_ar")
summary = batch.get_batch_summary(results)
```

## الخلاصة

هذا النظام يوفر حلاً احترافياً وشاملاً لترجمة التوثيقات التقنية إلى العربية، مع الحفاظ على الجودة العالية والدقة التقنية.

---

**آخر تحديث:** March 2025
