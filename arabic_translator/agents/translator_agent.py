"""
وكيل الترجمة
Translator Agent.

وكيل متخصص في الترجمة من الإنجليزية إلى العربية
Specialized agent for translating English to Arabic.
"""

from typing import Optional, Dict, Tuple
from ..glossary import GlossaryManager


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
        model: str = "gpt-4"
    ):
        """
        تهيئة وكيل الترجمة
        Initialize translator agent.

        Args:
            glossary_manager: مدير القاموس
            api_key: مفتاح API
            model: نموذج اللغة المستخدم
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.api_key = api_key
        self.model = model
        self.translation_history: Dict[str, str] = {}

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

        # Check history first
        if text in self.translation_history:
            return self.translation_history[text]

        # Create translation prompt with glossary context
        glossary_context = self._build_glossary_context(text)
        prompt = self._create_translation_prompt(text, glossary_context)

        # Simulate translation (in production, call actual LLM API)
        translation = self._call_llm_api(prompt)

        # Store in history
        self.translation_history[text] = translation

        return translation

    def translate_paragraph(self, paragraph: str) -> str:
        """
        ترجمة فقرة كاملة
        Translate a complete paragraph.

        Args:
            paragraph: الفقرة الإنجليزية

        Returns:
            str: الفقرة المترجمة
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

        Returns:
            str: النص المترجم مع مراعاة السياق
        """
        glossary_context = self._build_glossary_context(text, domain)
        prompt = self._create_contextual_prompt(text, context, glossary_context, domain)

        return self._call_llm_api(prompt)

    def _build_glossary_context(self, text: str, domain: str = "general") -> str:
        """
        بناء سياق القاموس من النص
        Build glossary context from text.

        Args:
            text: النص المراد تحليله
            domain: المجال

        Returns:
            str: سياق القاموس
        """
        words = text.lower().split()
        relevant_terms = []

        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,;:!?"\'')
            if len(clean_word) > 3:
                translation = self.glossary_manager.get_translation(clean_word)
                if translation:
                    relevant_terms.append(f"{clean_word} → {translation}")

        if relevant_terms:
            return "\n".join(relevant_terms[:10])
        return ""

    def _create_translation_prompt(self, text: str, glossary_context: str) -> str:
        """إنشاء prompt للترجمة"""
        return f"""أنت مترجم احترافي متخصص في التوثيقات التقنية.

ترجم النص التالي من الإنجليزية إلى العربية (اللهجة السعودية/الخليجية).

النص المراد ترجمته:
"{text}"

المصطلحات التقنية المهمة (استخدمها في الترجمة):
{glossary_context if glossary_context else "لا توجد مصطلحات محددة"}

التعليمات:
1. استخدم العربية الفصحى الحديثة مع لهجة خليجية طبيعية
2. احافظ على سياق التوثيقات التقنية
3. استخدم المصطلحات من القاموس إن أمكن
4. لا تترجم أسماء المكتبات والأدوات
5. اجعل الترجمة سلسة وسهلة القراءة

الترجمة:"""

    def _create_contextual_prompt(
        self,
        text: str,
        context: str,
        glossary: str,
        domain: str
    ) -> str:
        """إنشاء prompt مع السياق"""
        domain_instructions = self._get_domain_instructions(domain)

        return f"""أنت مترجم احترافي متخصص في التوثيقات التقنية للمجال: {domain}

السياق:
{context if context else "ترجمة توثيقات تقنية عامة"}

النص المراد ترجمته:
"{text}"

المصطلحات المتخصصة:
{glossary if glossary else "استخدم المصطلحات المتعارف عليها في المجال"}

{domain_instructions}

الترجمة:"""

    def _get_domain_instructions(self, domain: str) -> str:
        """الحصول على تعليمات خاصة بالمجال"""
        domain_guides = {
            "react": """
تذكر:
- Component = مكوّن
- State = الحالة
- Props = الخصائص
- Hook = خُطّاف
- Render = عرض/تصيير
- Virtual DOM = DOM افتراضي
""",
            "fastapi": """
تذكر:
- Endpoint = نقطة نهاية
- Route = مسار
- Request = طلب
- Response = رد
- Dependency = اعتماد
- Middleware = برمجيات وسيطة
""",
            "python": """
تذكر:
- Function = دالة
- Class = فئة
- Module = وحدة
- Import = استيراد
- Package = حزمة
- Exception = استثناء
""",
        }

        return domain_guides.get(domain, "")

    def _call_llm_api(self, prompt: str) -> str:
        """
        استدعاء واجهة LLM API
        Call LLM API.

        Args:
            prompt: prompt الترجمة

        Returns:
            str: الترجمة من LLM
        """
        # في الإنتاج، يتم استدعاء OpenAI أو Anthropic API هنا
        # For now, return a placeholder
        # In production, call actual LLM API

        # Example response (placeholder)
        return "[ترجمة مترجمة - في الإنتاج ستحصل على رد من LLM]"

    def batch_translate(self, texts: list) -> Dict[str, str]:
        """
        ترجمة مجموعة من النصوص
        Translate multiple texts.

        Args:
            texts: قائمة النصوص

        Returns:
            dict: قاموس بالترجمات
        """
        results = {}
        for text in texts:
            results[text] = self.translate_text(text)
        return results

    def get_translation_quality_hints(self, text: str) -> Dict[str, any]:
        """
        الحصول على تلميحات جودة الترجمة
        Get translation quality hints.

        Args:
            text: النص المراد تحليله

        Returns:
            dict: تلميحات الجودة
        """
        hints = {
            'technical_terms': [],
            'special_characters': [],
            'code_snippets': [],
            'abbreviations': [],
        }

        # Find technical terms
        for word in text.split():
            translation = self.glossary_manager.get_translation(word.lower().strip('.,;:!?"\''))
            if translation:
                hints['technical_terms'].append((word, translation))

        # Find special patterns
        import re
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
        }
