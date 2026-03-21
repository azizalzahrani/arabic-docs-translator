"""
اختبارات إدارة القاموس
Glossary Manager Tests.
"""

import pytest
import tempfile
import json
from pathlib import Path

from arabic_translator.glossary import GlossaryManager


class TestGlossaryManager:
    """فئة اختبار مدير القاموس"""

    @pytest.fixture
    def glossary(self):
        """إنشاء مدير قاموس للاختبار"""
        return GlossaryManager()

    def test_load_builtin_glossaries(self, glossary):
        """اختبار تحميل القواموس المدمجة"""
        assert "tech" in glossary.glossaries
        assert len(glossary.glossaries["tech"]) > 0

    def test_get_translation_existing_term(self, glossary):
        """اختبار الحصول على ترجمة مصطلح موجود"""
        translation = glossary.get_translation("api")
        assert translation is not None
        assert isinstance(translation, str)

    def test_get_translation_nonexistent_term(self, glossary):
        """اختبار الحصول على ترجمة مصطلح غير موجود"""
        translation = glossary.get_translation("nonexistent_xyz_term")
        assert translation is None

    def test_add_term(self, glossary):
        """اختبار إضافة مصطلح جديد"""
        glossary.add_term("test_term", "مصطلح اختبار")
        assert glossary.get_translation("test_term") == "مصطلح اختبار"

    def test_search_terms(self, glossary):
        """اختبار البحث عن المصطلحات"""
        results = glossary.search_terms("api")
        assert len(results) > 0
        assert "api" in results or any("api" in key.lower() for key in results.keys())

    def test_save_and_load_glossary(self, glossary):
        """اختبار حفظ وتحميل القاموس"""
        glossary.add_term("custom_term", "مصطلح مخصص")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save
            file_path = Path(tmpdir) / "test_glossary.json"
            glossary.save_glossary(str(file_path), "custom")

            assert file_path.exists()

            # Load
            new_glossary = GlossaryManager()
            new_glossary.load_custom_glossary(str(file_path), "loaded")

            assert new_glossary.get_translation("custom_term", "loaded") == "مصطلح مخصص"

    def test_glossary_size(self, glossary):
        """اختبار حجم القاموس"""
        sizes = glossary.get_glossary_size()
        assert "tech" in sizes
        assert sizes["tech"] > 0

    def test_list_all_terms(self, glossary):
        """اختبار قائمة جميع المصطلحات"""
        terms = glossary.list_all_terms("tech")
        assert len(terms) > 0
        assert isinstance(terms, list)

    def test_merge_glossaries(self, glossary):
        """اختبار دمج القواموس"""
        glossary.add_term("term1", "ترجمة1", "glossary1")
        glossary.add_term("term1", "ترجمة2", "glossary2")

        result = glossary.merge_glossaries("glossary1", "glossary2")
        assert result is True

    def test_case_insensitive_lookup(self, glossary):
        """اختبار البحث غير الحساس لحالة الأحرف"""
        glossary.add_term("TestTerm", "مصطلح اختبار")
        assert glossary.get_translation("testterm") == "مصطلح اختبار"
        assert glossary.get_translation("TESTTERM") == "مصطلح اختبار"

    def test_glossary_repr(self, glossary):
        """اختبار تمثيل القاموس"""
        repr_str = repr(glossary)
        assert "GlossaryManager" in repr_str
        assert "total_terms" in repr_str

    def test_get_all_translations(self, glossary):
        """اختبار الحصول على جميع الترجمات"""
        # Add same term to multiple glossaries
        glossary.add_term("react", "React", "custom1")
        glossary.add_term("react", "ريأكت", "custom2")

        all_translations = glossary.get_all_translations("react")
        assert "tech" in all_translations or "custom1" in all_translations

    def test_framework_terms(self, glossary):
        """اختبار المصطلحات الخاصة بالأطر"""
        assert "framework" in glossary.glossaries
        framework_terms = glossary.glossaries["framework"]
        assert len(framework_terms) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
