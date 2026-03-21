"""
مدير القاموس التقني
Glossary Manager for technical terms.

يدير تحميل وحفظ واستخدام القواموس التقنية
Manages loading, saving, and using technical glossaries.
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path


class GlossaryManager:
    """
    فئة إدارة القاموس
    Glossary manager class.

    تدير المصطلحات التقنية وتراجماتها وتوفر وظائف البحث
    Manages technical terms, their translations, and provides lookup functions.
    """

    def __init__(self, glossary_dir: Optional[str] = None):
        """
        تهيئة مدير القاموس
        Initialize the glossary manager.

        Args:
            glossary_dir: مسار مجلد القاموس (اختياري)
        """
        self.glossary_dir = glossary_dir or os.path.join(
            os.path.dirname(__file__)
        )
        self.glossaries: Dict[str, Dict[str, str]] = {}
        self._load_builtin_glossaries()

    def _load_builtin_glossaries(self) -> None:
        """
        تحميل القواموس المدمجة
        Load built-in glossaries.
        """
        try:
            # Load tech glossary
            tech_glossary_path = os.path.join(
                self.glossary_dir, "tech_glossary.json"
            )
            if os.path.exists(tech_glossary_path):
                with open(tech_glossary_path, "r", encoding="utf-8") as f:
                    self.glossaries["tech"] = json.load(f)

            # Load framework glossary
            framework_glossary_path = os.path.join(
                self.glossary_dir, "framework_terms.json"
            )
            if os.path.exists(framework_glossary_path):
                with open(framework_glossary_path, "r", encoding="utf-8") as f:
                    framework_data = json.load(f)
                    # Flatten framework glossary
                    self.glossaries["framework"] = self._flatten_dict(framework_data)
        except Exception as e:
            print(f"خطأ في تحميل القواموس المدمجة: {e}")

    def _flatten_dict(self, d: Dict, parent_key: str = "") -> Dict[str, str]:
        """
        تسطيح القاموس المتداخل
        Flatten nested dictionary.

        Args:
            d: القاموس المتداخل
            parent_key: مفتاح الأب

        Returns:
            dict: القاموس المسطح
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def load_custom_glossary(self, file_path: str, name: str = "custom") -> bool:
        """
        تحميل قاموس مخصص من ملف
        Load a custom glossary from file.

        Args:
            file_path: مسار ملف القاموس
            name: اسم القاموس

        Returns:
            bool: True إذا تم التحميل بنجاح، False وإلا
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                glossary = json.load(f)
                self.glossaries[name] = glossary
                return True
        except Exception as e:
            print(f"خطأ في تحميل القاموس المخصص: {e}")
            return False

    def add_term(
        self, term: str, translation: str, glossary_name: str = "custom"
    ) -> None:
        """
        إضافة مصطلح جديد إلى القاموس
        Add a new term to the glossary.

        Args:
            term: المصطلح الأصلي
            translation: الترجمة العربية
            glossary_name: اسم القاموس
        """
        if glossary_name not in self.glossaries:
            self.glossaries[glossary_name] = {}

        self.glossaries[glossary_name][term.lower()] = translation

    def get_translation(
        self, term: str, glossary_name: Optional[str] = None
    ) -> Optional[str]:
        """
        الحصول على ترجمة مصطلح
        Get translation for a term.

        Args:
            term: المصطلح المراد البحث عنه
            glossary_name: اسم القاموس (اختياري)

        Returns:
            str: الترجمة أو None إذا لم يتم العثور عليها
        """
        search_term = term.lower().strip()

        # Search in specific glossary if provided
        if glossary_name and glossary_name in self.glossaries:
            return self.glossaries[glossary_name].get(search_term)

        # Search in all glossaries (framework first, then tech)
        for name in ["framework", "custom", "tech"]:
            if name in self.glossaries:
                result = self.glossaries[name].get(search_term)
                if result:
                    return result

        return None

    def get_all_translations(self, term: str) -> Dict[str, str]:
        """
        الحصول على جميع ترجمات مصطلح من جميع القواموس
        Get all translations for a term from all glossaries.

        Args:
            term: المصطلح المراد البحث عنه

        Returns:
            dict: قاموس بأسماء القواموس والترجمات
        """
        search_term = term.lower().strip()
        results = {}

        for name, glossary in self.glossaries.items():
            if search_term in glossary:
                results[name] = glossary[search_term]

        return results

    def save_glossary(self, file_path: str, glossary_name: str = "custom") -> bool:
        """
        حفظ القاموس إلى ملف
        Save glossary to file.

        Args:
            file_path: مسار الملف
            glossary_name: اسم القاموس

        Returns:
            bool: True إذا تم الحفظ بنجاح، False وإلا
        """
        try:
            if glossary_name not in self.glossaries:
                print(f"القاموس '{glossary_name}' غير موجود")
                return False

            glossary = self.glossaries[glossary_name]
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(glossary, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"خطأ في حفظ القاموس: {e}")
            return False

    def merge_glossaries(
        self, target_name: str, source_name: str, overwrite: bool = False
    ) -> bool:
        """
        دمج قاموسين
        Merge two glossaries.

        Args:
            target_name: اسم القاموس الهدف
            source_name: اسم القاموس المصدر
            overwrite: هل يتم الكتابة فوق المصطلحات الموجودة

        Returns:
            bool: True إذا تم الدمج بنجاح، False وإلا
        """
        if source_name not in self.glossaries or target_name not in self.glossaries:
            return False

        source = self.glossaries[source_name]
        target = self.glossaries[target_name]

        for term, translation in source.items():
            if term not in target or overwrite:
                target[term] = translation

        return True

    def get_glossary_size(self, glossary_name: str = None) -> Dict[str, int]:
        """
        الحصول على حجم القاموس (عدد المصطلحات)
        Get glossary size (number of terms).

        Args:
            glossary_name: اسم القاموس (اختياري)

        Returns:
            dict: قاموس بأسماء القواموس وعدد المصطلحات
        """
        if glossary_name:
            if glossary_name in self.glossaries:
                return {glossary_name: len(self.glossaries[glossary_name])}
            return {}

        return {
            name: len(glossary) for name, glossary in self.glossaries.items()
        }

    def search_terms(self, pattern: str, glossary_name: Optional[str] = None) -> Dict[str, str]:
        """
        البحث عن مصطلحات تطابق نمط معين
        Search for terms matching a pattern.

        Args:
            pattern: النمط المراد البحث عنه
            glossary_name: اسم القاموس (اختياري)

        Returns:
            dict: قاموس بالمصطلحات والترجمات المطابقة
        """
        results = {}
        pattern_lower = pattern.lower()

        glossaries_to_search = (
            {glossary_name: self.glossaries[glossary_name]}
            if glossary_name and glossary_name in self.glossaries
            else self.glossaries
        )

        for glossary in glossaries_to_search.values():
            for term, translation in glossary.items():
                if pattern_lower in term.lower():
                    results[term] = translation

        return results

    def list_all_terms(self, glossary_name: Optional[str] = None) -> List[str]:
        """
        قائمة بجميع المصطلحات
        List all terms.

        Args:
            glossary_name: اسم القاموس (اختياري)

        Returns:
            list: قائمة بجميع المصطلحات
        """
        terms = []

        if glossary_name:
            if glossary_name in self.glossaries:
                terms.extend(self.glossaries[glossary_name].keys())
        else:
            for glossary in self.glossaries.values():
                terms.extend(glossary.keys())

        return sorted(list(set(terms)))

    def __repr__(self) -> str:
        """تمثيل نصي للكائن"""
        sizes = self.get_glossary_size()
        total = sum(sizes.values())
        return f"GlossaryManager(glossaries={len(self.glossaries)}, total_terms={total})"
