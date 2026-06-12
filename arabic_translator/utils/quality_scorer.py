"""
مقيّم جودة الترجمة
Translation Quality Scorer.

يقيّم جودة الترجمة بناءً على عدة معايير
Assesses translation quality based on multiple criteria.
"""

from typing import Dict, List, Optional
import re
from .text_utils import TextUtils
from ..glossary import GlossaryManager


class QualityScorer:
    """
    فئة تقييم جودة الترجمة
    Quality scorer class.

    تقيّم جودة الترجمة بناءً على:
    - استخدام مصطلحات القاموس
    - سلامة النصوص العربية
    - الحفاظ على تنسيق Markdown
    - عدم ترجمة الأكواد
    """

    def __init__(self, glossary_manager: Optional[GlossaryManager] = None):
        """
        تهيئة مقيّم الجودة
        Initialize the quality scorer.

        Args:
            glossary_manager: مدير القاموس (اختياري)
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.weights = {
            'glossary_usage': 0.3,
            'markdown_preservation': 0.2,
            'code_safety': 0.2,
            'text_quality': 0.2,
            'arabic_grammar': 0.1,
        }

    def score_translation(
        self,
        original: str,
        translated: str,
        original_language: str = "en",
        target_language: str = "ar"
    ) -> Dict[str, float]:
        """
        تقييم جودة الترجمة الشاملة
        Assess overall translation quality.

        Args:
            original: النص الأصلي
            translated: النص المترجم
            original_language: اللغة الأصلية
            target_language: اللغة الهدف

        Returns:
            dict: قاموس يحتوي على درجات وعلامة عامة
        """
        scores = {
            'glossary_usage': self._score_glossary_usage(original, translated),
            'markdown_preservation': self._score_markdown_preservation(original, translated),
            'code_safety': self._score_code_safety(original, translated),
            'text_quality': self._score_text_quality(translated),
            'arabic_grammar': self._score_arabic_grammar(translated),
        }

        # Calculate weighted final score
        final_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )

        return {
            **scores,
            'overall_score': round(final_score, 3),
            'scores_breakdown': scores,
        }

    def _score_glossary_usage(self, original: str, translated: str) -> float:
        """
        تقييم استخدام مصطلحات القاموس
        Score glossary term usage.

        Args:
            original: النص الأصلي
            translated: النص المترجم

        Returns:
            float: الدرجة من 0 إلى 1
        """
        if not original or not translated:
            return 0.0

        # Extract potential terms from original
        words = original.lower().split()
        glossary_matches = 0
        checked_terms = 0
        seen = set()

        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 3 and clean_word not in seen:
                seen.add(clean_word)
                translation = self.glossary_manager.get_translation(clean_word)
                if translation:
                    # Only words the glossary actually knows count toward the score
                    checked_terms += 1
                    if translation in translated:
                        glossary_matches += 1

        if checked_terms == 0:
            # No glossary terms expected -> nothing violated
            return 1.0

        return min(1.0, glossary_matches / checked_terms)

    def _score_markdown_preservation(self, original: str, translated: str) -> float:
        """
        تقييم حفظ تنسيق Markdown
        Score markdown preservation.

        Args:
            original: النص الأصلي
            translated: النص المترجم

        Returns:
            float: الدرجة من 0 إلى 1
        """
        original_elements = TextUtils.preserve_markdown_formatting(original)
        translated_elements = TextUtils.preserve_markdown_formatting(translated)

        # Check if headers are preserved
        original_headers_count = len(original_elements['headers'])
        translated_headers_count = len(translated_elements['headers'])

        # Check if code blocks are preserved
        original_code_count = len(original_elements['code_blocks'])
        translated_code_count = len(translated_elements['code_blocks'])

        # Check if links are preserved
        original_links_count = len(original_elements['links'])
        translated_links_count = len(translated_elements['links'])

        preservation_score = 0.0
        weights = 0

        if original_headers_count > 0:
            preservation_score += min(
                1.0,
                translated_headers_count / original_headers_count
            )
            weights += 1

        if original_code_count > 0:
            preservation_score += min(
                1.0,
                translated_code_count / original_code_count
            )
            weights += 1

        if original_links_count > 0:
            preservation_score += min(
                1.0,
                translated_links_count / original_links_count
            )
            weights += 1

        return preservation_score / weights if weights > 0 else 0.5

    def _score_code_safety(self, original: str, translated: str) -> float:
        """
        تقييم سلامة الأكواد (عدم ترجمة الكود)
        Score code safety (code not translated).

        Args:
            original: النص الأصلي
            translated: النص المترجم

        Returns:
            float: الدرجة من 0 إلى 1
        """
        code_blocks_original = TextUtils.extract_code_blocks(original)
        code_blocks_translated = TextUtils.extract_code_blocks(translated)

        if not code_blocks_original:
            return 1.0

        # Check if code blocks are preserved (should be identical)
        safety_score = 0.0
        for original_block in code_blocks_original:
            for translated_block in code_blocks_translated:
                # Code should be mostly identical
                similarity = self._calculate_similarity(
                    original_block.strip(),
                    translated_block.strip()
                )
                if similarity > 0.8:
                    safety_score += 1
                    break

        return min(1.0, safety_score / len(code_blocks_original))

    def _score_text_quality(self, translated: str) -> float:
        """
        تقييم جودة النص المترجم
        Score translated text quality.

        Args:
            translated: النص المترجم

        Returns:
            float: الدرجة من 0 إلى 1
        """
        if not translated:
            return 0.0

        # Check for common quality issues
        issues = 0
        total_checks = 5

        # 1. Check for excessive repetition
        words = translated.split()
        if len(words) > 0:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            max_freq = max(word_freq.values())
            if max_freq / len(words) > 0.3:
                issues += 1

        # 2. Check for unfinished sentences (Arabic and Latin enders)
        if not translated.strip().endswith(('.', '!', '?', '؟', '،', ':', '؛', '`')):
            issues += 1

        # 3. Check for proper spacing after punctuation
        if re.search(r'[.!?]\S', translated):
            issues += 1

        # 4. Check for balanced brackets/parentheses
        if translated.count('(') != translated.count(')'):
            issues += 1

        # 5. Check text length is reasonable compared to structure
        if len(translated.strip()) < 5:
            issues += 1

        return max(0.0, 1.0 - (issues / total_checks))

    def _score_arabic_grammar(self, translated: str) -> float:
        """
        تقييم سلامة القواعد اللغوية للعربية
        Score Arabic grammar correctness.

        Args:
            translated: النص المترجم

        Returns:
            float: الدرجة من 0 إلى 1
        """
        if not TextUtils.is_arabic(translated):
            return 0.5

        issues = 0
        total_checks = 4

        # 1. Check for proper Arabic diacritics usage
        # (not requiring them, but checking consistency)
        has_diacritics = bool(re.search(r'[\u064B-\u065F]', translated))
        has_no_diacritics = bool(re.search(r'[\u0600-\u06FF]', translated.replace('\u064B', '').replace('\u064C', '').replace('\u064D', '').replace('\u064E', '').replace('\u064F', '').replace('\u0650', '').replace('\u0651', '').replace('\u0652', '')))
        if has_diacritics and has_no_diacritics:
            issues += 1

        # 2. Check for proper space usage before Arabic punctuation
        if re.search(r'\S[،؛:؟!]', translated):
            issues += 0  # This is actually correct in Arabic

        # 3. Check for proper use of Arabic quotation marks
        if '"' in translated or "'" in translated:
            # English quotes in Arabic text is not ideal
            issues += 1

        # 4. Check for minimum text length
        if len(TextUtils.remove_extra_whitespace(translated)) < 3:
            issues += 1

        return max(0.0, 1.0 - (issues / total_checks))

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """
        حساب التشابه بين نصين
        Calculate similarity between two texts.

        Args:
            text1: النص الأول
            text2: النص الثاني

        Returns:
            float: درجة التشابه من 0 إلى 1
        """
        # Simple character-level similarity
        set1 = set(text1.lower())
        set2 = set(text2.lower())

        if not set1 or not set2:
            return float(text1 == text2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def get_quality_report(
        self,
        original: str,
        translated: str
    ) -> Dict:
        """
        الحصول على تقرير شامل لجودة الترجمة
        Get comprehensive quality report.

        Args:
            original: النص الأصلي
            translated: النص المترجم

        Returns:
            dict: تقرير شامل يتضمن درجات وتوصيات
        """
        scores = self.score_translation(original, translated)
        metrics_original = TextUtils.get_text_metrics(original)
        metrics_translated = TextUtils.get_text_metrics(translated)

        return {
            'scores': scores,
            'original_metrics': metrics_original,
            'translated_metrics': metrics_translated,
            'recommendations': self._generate_recommendations(scores),
        }

    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """
        توليد توصيات لتحسين الترجمة
        Generate recommendations for improvement.

        Args:
            scores: قاموس الدرجات

        Returns:
            list: قائمة بالتوصيات
        """
        recommendations = []

        if scores.get('glossary_usage', 1.0) < 0.7:
            recommendations.append(
                "استخدم المزيد من مصطلحات القاموس التقنية المتخصصة"
            )

        if scores.get('markdown_preservation', 1.0) < 0.8:
            recommendations.append(
                "تأكد من حفظ جميع عناصر Markdown (الرؤوس، الروابط، كتل الكود)"
            )

        if scores.get('code_safety', 1.0) < 0.9:
            recommendations.append(
                "تحقق من عدم ترجمة الأكواس البرمجية"
            )

        if scores.get('text_quality', 1.0) < 0.7:
            recommendations.append(
                "أعد صياغة النص لتحسين جودته وسهولة قراءته"
            )

        if scores.get('arabic_grammar', 1.0) < 0.7:
            recommendations.append(
                "راجع النص للتحقق من صحة القواعد اللغوية العربية"
            )

        return recommendations
