"""
وكيل الترجمة
Translator Agent.

وكيل متخصص في الترجمة من الإنجليزية إلى العربية
Specialized agent for translating English to Arabic.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..glossary import GlossaryManager
from ..providers import BaseProvider, DryRunProvider, create_provider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """أنت مترجم تقني محترف متخصص في توثيقات البرمجة.
You are a professional technical translator specialized in developer documentation.

ترجم من الإنجليزية إلى العربية الفصحى الحديثة بأسلوب طبيعي يناسب المطورين العرب.

قواعد صارمة:
1. أعد الترجمة فقط دون أي مقدمات أو شروحات أو علامات اقتباس إضافية.
2. لا تترجم أسماء المكتبات والأدوات والدوال (React, useState, npm, ...).
3. اترك أي نص بين علامتي backtick `...` كما هو تماماً دون ترجمة.
4. اترك العناصر النائبة مثل __CODE_BLOCK_1__ و __MDX_PLACEHOLDER_2__ كما هي حرفياً.
5. في روابط Markdown ‏[نص](رابط) ترجم النص فقط وأبقِ الرابط كما هو.
6. حافظ على رموز Markdown (العناوين #، القوائم -، الجداول |، الاقتباسات >).
7. استخدم المصطلحات المعتمدة في القاموس المرفق إن وجدت.
8. حافظ على فواصل الأسطر كما في النص الأصلي."""


class TranslatorAgent:
    """
    وكيل الترجمة
    Translator Agent class.

    يترجم النصوص من الإنجليزية إلى العربية مع استخدام القاموس
    Translates texts from English to Arabic using glossary.
    """

    def __init__(
        self,
        glossary_manager: Optional[GlossaryManager] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: str = "auto",
        temperature: float = 0.3,
        llm: Optional[BaseProvider] = None,
    ):
        """
        تهيئة وكيل الترجمة
        Initialize translator agent.

        Args:
            glossary_manager: مدير القاموس
            api_key: مفتاح API (اختياري، يتجاوز متغيرات البيئة)
            model: نموذج اللغة المستخدم ("auto" لاختيار الافتراضي)
            provider: openai | anthropic | none | auto
            temperature: درجة العشوائية
            llm: موفر جاهز (للاختبارات أو التخصيص المتقدم)
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.llm = llm or create_provider(
            provider=provider, model=model, temperature=temperature, api_key=api_key
        )
        self.model = self.llm.model
        self.translation_history: Dict[str, str] = {}

    @property
    def is_dry_run(self) -> bool:
        """هل الوكيل في الوضع التجريبي؟ | Whether the agent runs offline."""
        return isinstance(self.llm, DryRunProvider)

    def translate_text(self, text: str) -> str:
        """
        ترجمة نص واحد
        Translate a single text.

        Args:
            text: النص الإنجليزي المراد ترجمته

        Returns:
            str: النص المترجم إلى العربية
        """
        if not text or not text.strip():
            return ""

        # Translation memory: identical source segments translate identically.
        if text in self.translation_history:
            return self.translation_history[text]

        # Offline mode: return the source unchanged - never wrap it in prompts.
        if self.is_dry_run:
            self.translation_history[text] = text
            return text

        glossary_context = self._build_glossary_context(text)
        prompt = self._create_translation_prompt(text, glossary_context)

        translation = self.llm.complete_with_retry(SYSTEM_PROMPT, prompt)
        translation = self._clean_response(translation, text)

        self.translation_history[text] = translation
        return translation

    def translate_paragraph(self, paragraph: str) -> str:
        """
        ترجمة فقرة كاملة
        Translate a complete paragraph.
        """
        return self.translate_text(paragraph)

    def translate_with_context(
        self,
        text: str,
        context: str = "",
        domain: str = "general"
    ) -> str:
        """
        ترجمة مع السياق
        Translate with context awareness.

        Args:
            text: النص المراد ترجمته
            context: السياق الإضافي
            domain: المجال (react, fastapi, python, etc.)
        """
        if not text or not text.strip():
            return ""

        if self.is_dry_run:
            return text

        glossary_context = self._build_glossary_context(text, domain)
        prompt = self._create_contextual_prompt(text, context, glossary_context, domain)
        translation = self.llm.complete_with_retry(SYSTEM_PROMPT, prompt)
        return self._clean_response(translation, text)

    def _clean_response(self, translation: str, source: str) -> str:
        """
        تنظيف رد النموذج
        Clean up the model reply (stray quotes/labels some models add).
        """
        cleaned = translation.strip()

        # Strip a single pair of wrapping quotes if the source had none.
        if len(cleaned) >= 2 and cleaned[0] in '"«' and cleaned[-1] in '"»':
            if not (source.startswith('"') and source.endswith('"')):
                cleaned = cleaned[1:-1].strip()

        # Remove a leading "الترجمة:" label if a model echoes it back.
        cleaned = re.sub(r'^\s*(الترجمة|Translation)\s*[::]\s*', '', cleaned)

        return cleaned or source

    def _build_glossary_context(self, text: str, domain: str = "general") -> str:
        """
        بناء سياق القاموس من النص
        Build glossary context from text.
        """
        relevant_terms = []
        seen = set()

        # URLs and inline code are not translatable - keep their words out of context
        scannable = re.sub(r'`[^`\n]+`|https?://\S+|\]\([^)\s]+\)', ' ', text)
        words = re.findall(r"[A-Za-z][A-Za-z0-9_'-]*", scannable)

        # Single words
        for word in words:
            clean_word = word.lower()
            if clean_word in seen or len(clean_word) <= 2:
                continue
            translation = self.glossary_manager.get_translation(clean_word)
            if translation:
                seen.add(clean_word)
                relevant_terms.append(f"{clean_word} → {translation}")

        # Two-word terms (e.g. "virtual dom", "arrow function")
        lowered = [w.lower() for w in words]
        for first, second in zip(lowered, lowered[1:]):
            bigram = f"{first} {second}"
            if bigram in seen:
                continue
            translation = self.glossary_manager.get_translation(bigram)
            if translation:
                seen.add(bigram)
                relevant_terms.append(f"{bigram} → {translation}")

        return "\n".join(relevant_terms[:15])

    def _create_translation_prompt(self, text: str, glossary_context: str) -> str:
        """إنشاء prompt للترجمة"""
        glossary_section = (
            f"\n\nالمصطلحات المعتمدة:\n{glossary_context}" if glossary_context else ""
        )
        return f"""ترجم النص التالي إلى العربية:{glossary_section}

النص:
{text}"""

    def _create_contextual_prompt(
        self,
        text: str,
        context: str,
        glossary: str,
        domain: str
    ) -> str:
        """إنشاء prompt مع السياق"""
        domain_instructions = self._get_domain_instructions(domain)
        sections = []

        if context:
            sections.append(f"السياق:\n{context}")
        if glossary:
            sections.append(f"المصطلحات المعتمدة:\n{glossary}")
        if domain_instructions:
            sections.append(domain_instructions)

        prefix = ("\n\n".join(sections) + "\n\n") if sections else ""
        return f"""{prefix}ترجم النص التالي إلى العربية (المجال: {domain}):

النص:
{text}"""

    def _get_domain_instructions(self, domain: str) -> str:
        """الحصول على تعليمات خاصة بالمجال"""
        domain_guides = {
            "react": """تذكر:
- Component = مكوّن
- State = الحالة
- Props = الخصائص
- Hook = خُطّاف
- Render = تصيير
- Virtual DOM = DOM افتراضي""",
            "fastapi": """تذكر:
- Endpoint = نقطة نهاية
- Route = مسار
- Request = طلب
- Response = استجابة
- Dependency = اعتمادية
- Middleware = برمجيات وسيطة""",
            "python": """تذكر:
- Function = دالة
- Class = فئة
- Module = وحدة
- Import = استيراد
- Package = حزمة
- Exception = استثناء""",
        }
        return domain_guides.get(domain, "")

    def batch_translate(self, texts: List[str]) -> Dict[str, str]:
        """
        ترجمة مجموعة من النصوص
        Translate multiple texts.
        """
        return {text: self.translate_text(text) for text in texts}

    def get_translation_quality_hints(self, text: str) -> Dict[str, Any]:
        """
        الحصول على تلميحات جودة الترجمة
        Get translation quality hints.
        """
        hints: Dict[str, Any] = {
            'technical_terms': [],
            'special_characters': [],
            'code_snippets': [],
            'abbreviations': [],
        }

        for word in text.split():
            translation = self.glossary_manager.get_translation(
                word.lower().strip('.,;:!?"\'')
            )
            if translation:
                hints['technical_terms'].append((word, translation))

        hints['abbreviations'] = re.findall(r'\b[A-Z]{2,}\b', text)
        hints['code_snippets'] = re.findall(r'`[^`]+`', text)

        return hints

    def clear_history(self) -> None:
        """مسح سجل الترجمات"""
        self.translation_history.clear()

    def get_stats(self) -> Dict:
        """الحصول على إحصائيات الترجمة"""
        return {
            'total_translations': len(self.translation_history),
            'unique_translations': len(set(self.translation_history.values())),
            'provider': self.llm.name,
            'model': self.model,
        }
