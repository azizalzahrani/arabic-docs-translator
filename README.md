# مترجم التوثيقات التقنية للعربية
## Arabic Documentation Translator

---

## العربية 🇸🇦

### الوصف
**مترجم التوثيقات التقنية للعربية** هو أداة متقدمة متعددة الوكلاء (Multi-Agent Pipeline) لترجمة توثيقات المشاريع البرمجية من الإنجليزية إلى اللغة العربية عالية الجودة. لا تستخدم هذه الأداة ترجمة آلية عادية — بل تعتمد على ثلاث وكلاء متخصصين:

1. **وكيل الترجمة**: ترجمة احترافية من الإنجليزية إلى العربية
2. **وكيل المراجعة التقنية**: التحقق من الدقة التقنية والاتساق المصطلحي
3. **وكيل التكييف**: تكييف تعليقات الأكواد والتوطين الثقافي

### الميزات الرئيسية
- ✅ **حفظ تنسيق Markdown**: الرؤوس والروابط وجداول والقوائم المرقمة محفوظة تماماً
- ✅ **الأكواد البرمجية آمنة**: الأكواد تبقى بالإنجليزية، التعليقات فقط يتم ترجمتها
- ✅ **قاموس تقني ذكي**: 50+ مصطلح تقني متخصص مع ترجمات دقيقة
- ✅ **دعم MDX**: يدعم توثيقات React وNext.js مباشرة
- ✅ **معالجة دفعية**: ترجمة مجلدات كاملة من التوثيقات
- ✅ **تقييم الجودة**: درجة جودة لكل ترجمة
- ✅ **لغة عربية طبيعية**: لهجة عربية خليجية احترافية وطبيعية

### الأطر المدعومة
- React Documentation
- Next.js
- FastAPI
- Python Docs
- أي توثيقات بصيغة Markdown

---

### مثال قبل وبعد

#### ❌ ترجمة عادية (Google Translate):
```
النص الأصلي:
"The useState hook allows you to add state to functional components."

ترجمة سيئة:
"يسمح لك خطاف useState بإضافة الحالة إلى المكونات الوظيفية."
```

#### ✅ ترجمة احترافية (Arabic Docs Translator):
```
ترجمة احترافية:
"يتيح لك خُطّاف useState إضافة الحالة (State) إلى مكوّنات دالية (Functional Components)."
```

---

## English 🇺🇸

### Description
**Arabic Documentation Translator** is an advanced multi-agent pipeline for translating software documentation from English to professional-quality Arabic. This tool does not rely on standard machine translation — it uses three specialized agents:

1. **Translator Agent**: Professional English-to-Arabic translation
2. **Technical Reviewer Agent**: Technical accuracy and terminology consistency verification
3. **Adapter Agent**: Code comment adaptation and cultural localization

### Key Features
- ✅ **Markdown Format Preservation**: Headers, links, tables, and lists are fully preserved
- ✅ **Code Safety**: Code remains in English, only comments are translated
- ✅ **Smart Glossary**: 50+ technical terms with accurate translations
- ✅ **MDX Support**: Direct support for React and Next.js documentation
- ✅ **Batch Processing**: Translate entire documentation folders
- ✅ **Quality Scoring**: Quality score for each translation
- ✅ **Natural Arabic**: Professional Gulf/Saudi Arabic with natural phrasing

### Supported Frameworks
- React Documentation
- Next.js
- FastAPI
- Python Docs
- Any Markdown-based documentation

---

### Installation

```bash
git clone https://github.com/azizalzahrani/arabic-ai-toolkit
cd arabic-docs-translator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Add your API keys:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai
TRANSLATION_MODEL=gpt-4
```

### Quick Start

#### Translate a Single Markdown File
```python
from arabic_translator import DocumentTranslator

translator = DocumentTranslator()
result = translator.translate_file(
    input_path="docs/my_doc.md",
    output_path="docs/my_doc_ar.md"
)

print(f"Quality Score: {result['quality_score']}")
print(f"Translated: {result['output_path']}")
```

#### Batch Translate a Folder
```python
from arabic_translator import BatchTranslator

batch = BatchTranslator()
results = batch.translate_folder(
    input_folder="./docs/english",
    output_folder="./docs/arabic"
)

for file, result in results.items():
    print(f"{file}: Quality {result['quality_score']}")
```

#### Use Custom Glossary
```python
from arabic_translator.glossary import GlossaryManager

glossary = GlossaryManager()
glossary.add_term("my_term", "مصطلحي")
glossary.save("my_glossary.json")

# Use custom glossary
translator = DocumentTranslator(glossary_path="my_glossary.json")
```

### Project Architecture

```
Input Documentation
        ↓
   Markdown Parser (preserve structure)
        ↓
   Code Block Extractor (separate code from text)
        ↓
   Translator Agent (EN → AR with glossary)
        ↓
   Technical Reviewer (accuracy + terminology check)
        ↓
   Adapter Agent (code comments + localization)
        ↓
   Quality Scorer (assess translation quality)
        ↓
   Markdown Reconstructor
        ↓
Output (Arabic Documentation)
```

### API Documentation

#### `DocumentTranslator`
Main translator class for single files.

```python
translator = DocumentTranslator(
    glossary_path="glossary.json",
    quality_threshold=0.8,
    model="gpt-4"
)

result = translator.translate_file(
    input_path="docs/readme.md",
    output_path="docs/readme_ar.md",
    language="ar"
)

# Result contains:
# - 'output_path': path to translated file
# - 'quality_score': float between 0 and 1
# - 'terminology_matches': int count of glossary terms used
# - 'translation_time': float seconds
```

#### `BatchTranslator`
Process multiple files efficiently.

```python
batch = BatchTranslator(num_workers=4)
results = batch.translate_folder(
    input_folder="docs",
    output_folder="docs_ar",
    file_pattern="*.md"
)
```

#### `GlossaryManager`
Manage technical terminology.

```python
glossary = GlossaryManager()
glossary.load("tech_glossary.json")
glossary.add_term("component", "مكوّن")
glossary.get_translation("component")  # Returns "مكوّن"
glossary.save("custom.json")
```

### Supported File Types
- `.md` - Markdown files
- `.mdx` - MDX (React documentation)
- `.rst` - reStructuredText (with conversion)

### Translation Quality

Quality scores are calculated based on:
- ✅ Proper glossary term usage
- ✅ Markdown format preservation
- ✅ Arabic grammar and syntax validation
- ✅ No untranslated technical jargon
- ✅ Code block integrity

**Minimum threshold**: 0.8 (configurable)

### Glossary Management

The tool includes built-in glossaries for:
- **General Technical Terms**: 50+ common programming terms
- **React/Next.js**: Component, Props, Hooks, State management
- **FastAPI**: Route, Endpoint, Request, Response, Dependency
- **Python**: Class, Function, Method, Module, Package

You can extend with custom glossaries:
```python
{
  "custom_term": "مصطلح مخصص",
  "api_gateway": "بوابة واجهة البرمجة"
}
```

### Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### License
MIT License - see LICENSE file for details

### Support

- 📧 Email: [your-email]
- 🐛 Report bugs: [GitHub Issues]
- 💡 Request features: [GitHub Discussions]

### Roadmap

- [ ] Support for more languages (French, Urdu, Turkish)
- [ ] Web UI for translation
- [ ] API server for remote translation
- [ ] Integration with documentation platforms (MkDocs, Docusaurus)
- [ ] Translation memory for consistency
- [ ] Real-time collaboration features

---

**Made with ❤️ for the Arabic developer community**

Part of the **arabic-ai-toolkit** series by [azizalzahrani](https://github.com/azizalzahrani)
