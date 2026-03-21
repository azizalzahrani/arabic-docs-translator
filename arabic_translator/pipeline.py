"""
خط أنابيب الترجمة
Translation Pipeline.

خط أنابيب متعدد الوكلاء للترجمة الاحترافية
Multi-agent pipeline for professional translation.
"""

import os
from typing import Dict, Optional, List, Tuple
from pathlib import Path

from .config import config
from .agents import TranslatorAgent, ReviewerAgent, AdapterAgent
from .parsers import MarkdownParser, CodeBlockHandler, MDXParser
from .glossary import GlossaryManager
from .utils import TextUtils, QualityScorer


class DocumentTranslator:
    """
    فئة مترجم المستندات
    Document translator class.

    ترجم مستند واحد عبر خط الأنابيب الكامل
    Translates a single document through the complete pipeline.
    """

    def __init__(
        self,
        glossary_path: Optional[str] = None,
        quality_threshold: float = 0.8,
        model: str = "gpt-4"
    ):
        """
        تهيئة المترجم
        Initialize document translator.

        Args:
            glossary_path: مسار القاموس المخصص
            quality_threshold: حد الجودة الأدنى
            model: نموذج اللغة
        """
        self.config = config
        self.quality_threshold = quality_threshold
        self.model = model

        # Initialize glossary
        self.glossary = GlossaryManager()
        if glossary_path:
            self.glossary.load_custom_glossary(glossary_path)

        # Initialize agents
        self.translator = TranslatorAgent(self.glossary, model=model)
        self.reviewer = ReviewerAgent(self.glossary)
        self.adapter = AdapterAgent(self.glossary, model=model)

        # Initialize parsers
        self.markdown_parser = MarkdownParser()
        self.code_handler = CodeBlockHandler()
        self.mdx_parser = MDXParser()

        # Quality scorer
        self.quality_scorer = QualityScorer(self.glossary)

    def translate_file(
        self,
        input_path: str,
        output_path: str,
        file_type: Optional[str] = None
    ) -> Dict:
        """
        ترجمة ملف واحد
        Translate a single file.

        Args:
            input_path: مسار الملف المراد ترجمته
            output_path: مسار الملف المترجم
            file_type: نوع الملف (auto-detect if not provided)

        Returns:
            dict: نتائج الترجمة والجودة
        """
        # Read input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Detect file type
        if not file_type:
            file_type = self._detect_file_type(input_path)

        # Translate based on file type
        if file_type == 'mdx':
            translated = self._translate_mdx(content)
        elif file_type == 'md':
            translated = self._translate_markdown(content)
        else:
            translated = self._translate_plain_text(content)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

        # Score quality
        quality_report = self.quality_scorer.score_translation(content, translated)

        return {
            'status': 'success',
            'input_path': input_path,
            'output_path': output_path,
            'file_type': file_type,
            'quality_score': quality_report['overall_score'],
            'quality_report': quality_report,
            'quality_passed': quality_report['overall_score'] >= self.quality_threshold,
            'translation_time': 0.0,  # Would be measured in production
        }

    def _translate_markdown(self, content: str) -> str:
        """ترجمة ملف Markdown"""
        # Parse markdown
        elements = self.markdown_parser.parse(content)

        # Translate text elements
        translated_elements = []
        for element in elements:
            if element.type in ['header', 'paragraph', 'blockquote']:
                translated_content = self.translator.translate_text(element.content)
                translated_content = self.adapter.adapt_translation(translated_content)
                element.content = translated_content

            elif element.type == 'list':
                # Translate list items
                items = element.content.split('\n')
                translated_items = []
                for item in items:
                    match = element.content  # Would extract item properly in production
                    if match:
                        # Extract list marker and content
                        import re
                        list_match = re.match(r'^(\s*[-*+]\s+)(.+)$', item)
                        if list_match:
                            marker = list_match.group(1)
                            item_text = list_match.group(2)
                            translated_text = self.translator.translate_text(item_text)
                            translated_text = self.adapter.adapt_translation(translated_text)
                            translated_items.append(f'{marker}{translated_text}')
                        else:
                            translated_items.append(item)

                element.content = '\n'.join(translated_items)

            translated_elements.append(element)

        # Reconstruct markdown
        return self.markdown_parser.reconstruct(translated_elements)

    def _translate_mdx(self, content: str) -> str:
        """ترجمة ملف MDX"""
        # Parse MDX
        elements, protected = self.mdx_parser.parse(content)

        # Translate text elements
        for element in elements:
            if element.type in ['header', 'paragraph', 'blockquote']:
                translated = self.translator.translate_text(element.content)
                element.content = self.adapter.adapt_translation(translated)

        # Reconstruct
        reconstructed = self.markdown_parser.reconstruct(elements)

        # Restore protected elements
        return self.mdx_parser.restore(reconstructed)

    def _translate_plain_text(self, content: str) -> str:
        """ترجمة نص عادي"""
        # Extract code blocks first
        protected, code_blocks = self.code_handler.extract_code_blocks(content)

        # Translate remaining text
        translated = self.translator.translate_text(protected)
        translated = self.adapter.adapt_translation(translated)

        # Restore code blocks
        for placeholder, block in code_blocks.items():
            translated = translated.replace(placeholder, block.code)

        return translated

    def _detect_file_type(self, file_path: str) -> str:
        """الكشف عن نوع الملف"""
        extension = Path(file_path).suffix.lower()

        if extension == '.mdx':
            return 'mdx'
        elif extension == '.md':
            return 'md'
        else:
            return 'text'

    def translate_with_review(
        self,
        input_path: str,
        output_path: str
    ) -> Dict:
        """
        ترجمة مع المراجعة الكاملة
        Translate with full review process.

        Args:
            input_path: مسار الملف المراد ترجمته
            output_path: مسار الملف المترجم

        Returns:
            dict: نتائج الترجمة والمراجعة
        """
        # Translate
        translation_result = self.translate_file(input_path, output_path)

        # Read translated file
        with open(output_path, 'r', encoding='utf-8') as f:
            translated_content = f.read()

        # Read original file
        with open(input_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Review
        review_result = self.reviewer.review_translation(
            original_content,
            translated_content
        )

        return {
            **translation_result,
            'review': review_result,
            'approved': review_result['overall_approval'],
        }


class BatchTranslator:
    """
    فئة الترجمة الدفعية
    Batch translator class.

    ترجمة مجلدات كاملة من الملفات
    Translates entire folders of files.
    """

    def __init__(
        self,
        glossary_path: Optional[str] = None,
        num_workers: int = 4,
        quality_threshold: float = 0.8
    ):
        """
        تهيئة الترجمة الدفعية
        Initialize batch translator.

        Args:
            glossary_path: مسار القاموس المخصص
            num_workers: عدد العمليات المتوازية
            quality_threshold: حد الجودة
        """
        self.translator = DocumentTranslator(glossary_path, quality_threshold)
        self.num_workers = num_workers

    def translate_folder(
        self,
        input_folder: str,
        output_folder: str,
        file_pattern: str = "*.md",
        recursive: bool = True
    ) -> Dict[str, Dict]:
        """
        ترجمة مجلد كامل
        Translate entire folder.

        Args:
            input_folder: مسار المجلد المراد ترجمته
            output_folder: مسار المجلد المترجم
            file_pattern: نمط الملفات المراد ترجمتها
            recursive: هل يتم البحث المتكرر في المجلدات الفرعية

        Returns:
            dict: قاموس بنتائج كل ملف
        """
        results = {}
        input_path = Path(input_folder)

        # Find matching files
        if recursive:
            files = list(input_path.rglob(file_pattern))
        else:
            files = list(input_path.glob(file_pattern))

        # Translate each file
        for input_file in files:
            relative_path = input_file.relative_to(input_path)
            output_file = Path(output_folder) / relative_path

            try:
                result = self.translator.translate_file(
                    str(input_file),
                    str(output_file)
                )
                results[str(relative_path)] = result
            except Exception as e:
                results[str(relative_path)] = {
                    'status': 'error',
                    'error': str(e),
                }

        return results

    def get_batch_summary(self, results: Dict[str, Dict]) -> Dict:
        """
        الحصول على ملخص الدفعة
        Get batch translation summary.

        Args:
            results: نتائج الترجمة

        Returns:
            dict: ملخص الدفعة
        """
        total = len(results)
        successful = sum(1 for r in results.values() if r.get('status') == 'success')
        failed = total - successful
        avg_quality = (
            sum(r.get('quality_score', 0) for r in results.values() if r.get('status') == 'success')
            / successful
            if successful > 0
            else 0
        )

        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0,
            'average_quality_score': avg_quality,
            'high_quality_files': sum(
                1 for r in results.values()
                if r.get('quality_passed', False)
            ),
        }
