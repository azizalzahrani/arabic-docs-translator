"""
وكيل المراجعة التقنية
Technical Reviewer Agent.

يراجع دقة الترجمة التقنية والاتساق المصطلحي
Reviews technical accuracy and terminology consistency.
"""

import re
from typing import Dict, List, Optional
from ..glossary import GlossaryManager


class ReviewerAgent:
    """
    وكيل المراجعة التقنية
    Technical reviewer agent class.

    يراجع الترجمات للتحقق من الدقة التقنية والاتساق المصطلحي
    Reviews translations for technical accuracy and terminology consistency.
    """

    def __init__(self, glossary_manager: Optional[GlossaryManager] = None):
        """
        تهيئة وكيل المراجعة
        Initialize reviewer agent.

        Args:
            glossary_manager: مدير القاموس
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.review_history: List[Dict] = []

    def review_translation(
        self,
        original: str,
        translated: str
    ) -> Dict:
        """
        مراجعة ترجمة واحدة
        Review a single translation.

        Args:
            original: النص الأصلي
            translated: النص المترجم

        Returns:
            dict: تقرير المراجعة
        """
        review_report = {
            'original': original,
            'translated': translated,
            'issues': [],
            'suggestions': [],
            'consistency_score': 0.0,
            'technical_accuracy': 0.0,
            'overall_approval': False,
        }

        # Check terminology consistency
        consistency = self._check_terminology_consistency(original, translated)
        review_report['consistency_score'] = consistency['score']
        review_report['issues'].extend(consistency['issues'])
        review_report['suggestions'].extend(consistency['suggestions'])

        # Check technical accuracy
        accuracy = self._check_technical_accuracy(original, translated)
        review_report['technical_accuracy'] = accuracy['score']
        review_report['issues'].extend(accuracy['issues'])
        review_report['suggestions'].extend(accuracy['suggestions'])

        # Check for untranslated terms
        untranslated = self._find_untranslated_terms(translated)
        if untranslated:
            review_report['issues'].append(f"Untranslated terms found: {untranslated}")

        # Determine overall approval
        avg_score = (review_report['consistency_score'] + review_report['technical_accuracy']) / 2
        review_report['overall_approval'] = avg_score >= 0.8

        self.review_history.append(review_report)
        return review_report

    def _check_terminology_consistency(self, original: str, translated: str) -> Dict:
        """التحقق من اتساق المصطلحات"""
        issues = []
        suggestions = []
        consistency_matches = 0
        total_glossary_terms = 0

        # Extract terms from original
        words = original.lower().split()
        for word in words:
            clean_word = word.strip('.,;:!?"\'')
            if len(clean_word) > 3:
                translation = self.glossary_manager.get_translation(clean_word)
                if translation:
                    total_glossary_terms += 1
                    if translation in translated:
                        consistency_matches += 1
                    else:
                        issues.append(f"Expected '{translation}' for '{clean_word}' not found")
                        suggestions.append(f"Use '{translation}' instead of alternative translation")

        score = (
            consistency_matches / total_glossary_terms
            if total_glossary_terms > 0
            else 1.0
        )

        return {
            'score': score,
            'issues': issues,
            'suggestions': suggestions,
            'matches': consistency_matches,
            'total_terms': total_glossary_terms,
        }

    def _check_technical_accuracy(self, original: str, translated: str) -> Dict:
        """التحقق من الدقة التقنية"""
        issues = []
        suggestions = []

        # Check for code preservation (a block has an opening and closing fence)
        code_blocks_original = original.count('```') // 2
        code_blocks_translated = translated.count('```') // 2

        if code_blocks_original != code_blocks_translated:
            issues.append(
                f"Code block count mismatch: {code_blocks_original} vs {code_blocks_translated}"
            )
            suggestions.append("Ensure all code blocks are preserved in translation")

        # Check for proper markdown preservation
        links_original = original.count('[')
        links_translated = translated.count('[')

        if links_original != links_translated:
            issues.append(
                f"Link count mismatch: {links_original} vs {links_translated}"
            )
            suggestions.append("Ensure all markdown links are preserved")

        # Check for balanced parentheses/brackets
        if original.count('(') != translated.count('('):
            issues.append("Parentheses mismatch detected")

        score = max(0.0, 1.0 - (len(issues) * 0.2))

        return {
            'score': score,
            'issues': issues,
            'suggestions': suggestions,
        }

    def _find_untranslated_terms(self, text: str) -> List[str]:
        """البحث عن المصطلحات غير المترجمة"""
        untranslated = []

        # Common English technical terms
        technical_terms = [
            'function', 'class', 'variable', 'array', 'object', 'string',
            'boolean', 'integer', 'float', 'null', 'undefined', 'const',
            'let', 'var', 'import', 'export', 'return', 'async', 'await',
            'promise', 'callback', 'arrow', 'spread', 'destructure',
        ]

        text_lower = text.lower()
        for term in technical_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                # Check if it's not inside inline code
                if not self._is_in_code_block(text, term):
                    untranslated.append(term)

        return untranslated

    def _is_in_code_block(self, text: str, term: str) -> bool:
        """التحقق من كون المصطلح داخل كتلة كود"""
        # Simple check: if surrounded by backticks
        pattern = f'`[^`]*{re.escape(term)}[^`]*`'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def batch_review(
        self,
        originals: List[str],
        translations: List[str]
    ) -> List[Dict]:
        """
        مراجعة مجموعة من الترجمات
        Review multiple translations.

        Args:
            originals: قائمة النصوص الأصلية
            translations: قائمة الترجمات

        Returns:
            list: قائمة تقارير المراجعة
        """
        reviews = []
        for original, translation in zip(originals, translations):
            review = self.review_translation(original, translation)
            reviews.append(review)
        return reviews

    def get_critical_issues(self) -> List[Dict]:
        """الحصول على المشاكل الحرجة من السجل"""
        critical = []
        for review in self.review_history:
            if not review['overall_approval']:
                critical.append({
                    'text': review['original'],
                    'issues': review['issues'],
                    'suggestions': review['suggestions'],
                })
        return critical

    def generate_review_report(self) -> Dict:
        """توليد تقرير مراجعة شامل"""
        if not self.review_history:
            return {'total_reviews': 0, 'message': 'No reviews yet'}

        total = len(self.review_history)
        approved = sum(1 for r in self.review_history if r['overall_approval'])
        avg_consistency = sum(r['consistency_score'] for r in self.review_history) / total
        avg_accuracy = sum(r['technical_accuracy'] for r in self.review_history) / total

        return {
            'total_reviews': total,
            'approved': approved,
            'rejected': total - approved,
            'approval_rate': approved / total if total > 0 else 0,
            'average_consistency_score': avg_consistency,
            'average_technical_accuracy': avg_accuracy,
            'critical_issues': len(self.get_critical_issues()),
        }

    def suggest_improvements(self, review_report: Dict) -> List[str]:
        """
        اقتراح تحسينات بناءً على التقرير
        Suggest improvements based on review.

        Args:
            review_report: تقرير المراجعة

        Returns:
            list: قائمة الاقتراحات
        """
        suggestions = review_report.get('suggestions', [])

        if review_report['consistency_score'] < 0.7:
            suggestions.append(
                "Review glossary usage and ensure consistent terminology"
            )

        if review_report['technical_accuracy'] < 0.7:
            suggestions.append(
                "Check code blocks and markdown formatting preservation"
            )

        return suggestions

    def clear_history(self) -> None:
        """مسح سجل المراجعات"""
        self.review_history.clear()

    def get_stats(self) -> Dict:
        """الحصول على إحصائيات المراجعة"""
        return self.generate_review_report()
