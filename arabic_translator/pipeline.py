"""
خط أنابيب الترجمة
Translation Pipeline.

خط أنابيب متعدد الوكلاء للترجمة الاحترافية
Multi-agent pipeline for professional translation.
"""

import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import config
from .agents import TranslatorAgent, ReviewerAgent, AdapterAgent
from .parsers import MarkdownParser, CodeBlockHandler, MDXParser
from .parsers.markdown_parser import MarkdownElement
from .glossary import GlossaryManager
from .utils import QualityScorer

logger = logging.getLogger(__name__)

# YAML frontmatter at the very start of a document
_FRONTMATTER_PATTERN = re.compile(r'\A(---\n.*?\n---\n)', re.DOTALL)

# List item markers: unordered (-, *, +) and ordered (1. / 1))
_LIST_ITEM_PATTERN = re.compile(r'^(\s*(?:[-*+]|\d+[.)])\s+)(.+)$')

#: Element types whose content goes through the translator
_TRANSLATABLE_TYPES = ('header', 'paragraph', 'blockquote')


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
        model: Optional[str] = None,
        provider: str = "auto",
    ):
        """
        تهيئة المترجم
        Initialize document translator.

        Args:
            glossary_path: مسار القاموس المخصص
            quality_threshold: حد الجودة الأدنى
            model: نموذج اللغة ("auto" أو None لاختيار الافتراضي)
            provider: openai | anthropic | none | auto
        """
        self.config = config
        self.quality_threshold = quality_threshold

        # Initialize glossary
        self.glossary = GlossaryManager()
        if glossary_path:
            self.glossary.load_custom_glossary(glossary_path)

        # Initialize agents
        self.translator = TranslatorAgent(self.glossary, model=model, provider=provider)
        self.reviewer = ReviewerAgent(self.glossary)
        self.adapter = AdapterAgent(self.glossary)
        self.model = self.translator.model

        # Initialize parsers
        self.markdown_parser = MarkdownParser()
        self.code_handler = CodeBlockHandler()
        self.mdx_parser = MDXParser()

        # Quality scorer
        self.quality_scorer = QualityScorer(self.glossary)

        if self.translator.is_dry_run:
            logger.warning(
                "DocumentTranslator is in DRY-RUN mode (no API key configured): "
                "files are processed but text is not translated."
            )

    @property
    def is_dry_run(self) -> bool:
        """هل المترجم في الوضع التجريبي؟ | Whether translation runs offline."""
        return self.translator.is_dry_run

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
        started = time.perf_counter()

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not file_type:
            file_type = self._detect_file_type(input_path)

        # Keep YAML frontmatter untouched (titles/keys must stay machine-readable)
        frontmatter, body = self._split_frontmatter(content)

        if file_type == 'mdx':
            translated = self._translate_mdx(body)
        elif file_type == 'md':
            translated = self._translate_markdown(body)
        else:
            translated = self._translate_plain_text(body)

        if frontmatter and not translated.startswith('\n'):
            translated = frontmatter + '\n' + translated
        else:
            translated = frontmatter + translated

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

        quality_report = self.quality_scorer.score_translation(content, translated)
        elapsed = time.perf_counter() - started

        return {
            'status': 'success',
            'input_path': input_path,
            'output_path': output_path,
            'file_type': file_type,
            'dry_run': self.is_dry_run,
            'quality_score': quality_report['overall_score'],
            'quality_report': quality_report,
            'quality_passed': quality_report['overall_score'] >= self.quality_threshold,
            'translation_time': round(elapsed, 3),
        }

    @staticmethod
    def _split_frontmatter(content: str) -> Tuple[str, str]:
        """فصل frontmatter عن المتن | Split YAML frontmatter from the body."""
        match = _FRONTMATTER_PATTERN.match(content)
        if match:
            return match.group(1), content[match.end():]
        return '', content

    def _translate_elements(self, elements: List[MarkdownElement]) -> List[MarkdownElement]:
        """
        ترجمة عناصر Markdown النصية في مكانها
        Translate text-bearing markdown elements in place.
        """
        for element in elements:
            if element.type in _TRANSLATABLE_TYPES:
                translated = self.translator.translate_text(element.content)
                element.content = self.adapter.adapt_translation(translated)

            elif element.type == 'list':
                element.content = self._translate_list(element.content)

        return elements

    def _translate_list(self, list_content: str) -> str:
        """ترجمة عناصر قائمة (مرقمة وغير مرقمة) | Translate ordered and unordered list items."""
        translated_items = []
        for item in list_content.split('\n'):
            match = _LIST_ITEM_PATTERN.match(item)
            if match:
                marker, item_text = match.group(1), match.group(2)
                translated_text = self.translator.translate_text(item_text)
                translated_text = self.adapter.adapt_translation(translated_text)
                translated_items.append(f'{marker}{translated_text}')
            else:
                translated_items.append(item)
        return '\n'.join(translated_items)

    def _translate_markdown(self, content: str) -> str:
        """ترجمة ملف Markdown"""
        elements = self.markdown_parser.parse(content)
        elements = self._translate_elements(elements)
        return self.markdown_parser.reconstruct(elements)

    def _translate_mdx(self, content: str) -> str:
        """ترجمة ملف MDX"""
        elements, _protected = self.mdx_parser.parse(content)
        elements = self._translate_elements(elements)
        reconstructed = self.markdown_parser.reconstruct(elements)
        return self.mdx_parser.restore(reconstructed)

    def _translate_plain_text(self, content: str) -> str:
        """ترجمة نص عادي"""
        protected, code_blocks = self.code_handler.extract_code_blocks(content)

        translated = self.translator.translate_text(protected)
        translated = self.adapter.adapt_translation(translated)

        return self.code_handler.restore_code_blocks(translated, code_blocks)

    def _detect_file_type(self, file_path: str) -> str:
        """الكشف عن نوع الملف"""
        extension = Path(file_path).suffix.lower()
        if extension == '.mdx':
            return 'mdx'
        if extension in ('.md', '.markdown'):
            return 'md'
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
        translation_result = self.translate_file(input_path, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            translated_content = f.read()
        with open(input_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

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

    ترجمة مجلدات كاملة من الملفات بالتوازي
    Translates entire folders of files in parallel.
    """

    def __init__(
        self,
        glossary_path: Optional[str] = None,
        num_workers: int = 4,
        quality_threshold: float = 0.8,
        model: Optional[str] = None,
        provider: str = "auto",
    ):
        """
        تهيئة الترجمة الدفعية
        Initialize batch translator.

        Args:
            glossary_path: مسار القاموس المخصص
            num_workers: عدد الخيوط المتوازية
            quality_threshold: حد الجودة
            model: نموذج اللغة
            provider: openai | anthropic | none | auto
        """
        self.translator = DocumentTranslator(
            glossary_path,
            quality_threshold,
            model=model,
            provider=provider,
        )
        self.num_workers = max(1, int(num_workers))

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
        results: Dict[str, Dict] = {}
        input_path = Path(input_folder)
        output_path = Path(output_folder).resolve()

        files = list(input_path.rglob(file_pattern)) if recursive else list(input_path.glob(file_pattern))

        # Never re-translate our own output when it nests inside the input folder
        files = [
            f for f in files
            if output_path not in f.resolve().parents and f.resolve() != output_path
        ]

        def worker(input_file: Path) -> Tuple[str, Dict]:
            relative = input_file.relative_to(input_path)
            target = Path(output_folder) / relative
            try:
                result = self.translator.translate_file(str(input_file), str(target))
            except Exception as exc:  # noqa: BLE001 - report per-file failures
                logger.exception("Failed to translate %s", input_file)
                result = {'status': 'error', 'error': str(exc)}
            return str(relative), result

        if self.num_workers == 1 or len(files) <= 1:
            for input_file in files:
                key, result = worker(input_file)
                results[key] = result
        else:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures = {executor.submit(worker, f): f for f in files}
                for future in as_completed(futures):
                    key, result = future.result()
                    results[key] = result

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
            'average_quality_score': round(avg_quality, 3),
            'high_quality_files': sum(
                1 for r in results.values()
                if r.get('quality_passed', False)
            ),
        }
