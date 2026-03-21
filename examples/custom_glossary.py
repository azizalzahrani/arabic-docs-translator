#!/usr/bin/env python3
"""
مثال: استخدام قاموس مخصص
Example: Using Custom Glossary.

يوضح كيفية إنشاء واستخدام قاموس مخصص
Demonstrates how to create and use a custom glossary.
"""

from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arabic_translator import GlossaryManager, DocumentTranslator


def create_custom_glossary():
    """إنشاء قاموس مخصص"""
    custom_glossary = {
        "component": "مكوّن",
        "state": "الحالة",
        "props": "الخصائص",
        "hook": "خُطّاف",
        "render": "عرض/تصيير",
        "virtual_dom": "DOM افتراضي",
        "functional_component": "مكوّن دالي",
        "class_component": "مكوّن صفي",
        "lifecycle": "دورة الحياة",
        "ref": "مرجع",
        "context": "السياق",
        "provider": "موفر",
        "consumer": "مستهلك",
        "effect": "مفعول",
        "dependency": "اعتماد",
        "fragment": "شظية",
        "portal": "بوابة",
        "suspense": "انتظار",
        "lazy": "تحميل كسول",
        "error_boundary": "حد الخطأ",
    }

    return custom_glossary


def main():
    """الدالة الرئيسية"""
    print("📚 Custom Glossary Example")
    print("=" * 50)

    # Initialize glossary manager
    glossary = GlossaryManager()

    # Show built-in glossary stats
    print(f"\n📖 Built-in Glossaries:")
    builtin_sizes = glossary.get_glossary_size()
    for name, size in builtin_sizes.items():
        print(f"  - {name}: {size} terms")

    # Create custom glossary
    print(f"\n✏️ Creating custom glossary...")
    custom_glossary = create_custom_glossary()

    # Add custom terms
    for term, translation in custom_glossary.items():
        glossary.add_term(term, translation, "react_custom")

    print(f"✅ Added {len(custom_glossary)} custom terms")

    # Show updated stats
    print(f"\n📊 Updated Glossary Stats:")
    sizes = glossary.get_glossary_size()
    for name, size in sizes.items():
        print(f"  - {name}: {size} terms")

    # Test term lookups
    print(f"\n🔍 Testing Term Lookups:")
    print("-" * 50)

    test_terms = ["component", "state", "props", "hook", "react"]
    for term in test_terms:
        translation = glossary.get_translation(term)
        if translation:
            print(f"  {term} → {translation}")
        else:
            print(f"  {term} → [Not found]")

    # Search for terms with pattern
    print(f"\n🔎 Search Results for 'com':")
    print("-" * 50)
    search_results = glossary.search_terms("com")
    for term, translation in search_results.items():
        print(f"  {term} → {translation}")

    # List all React terms
    print(f"\n📋 React Custom Glossary Terms:")
    print("-" * 50)
    react_terms = glossary.list_all_terms("react_custom")
    for term in sorted(react_terms):
        translation = glossary.get_translation(term, "react_custom")
        print(f"  {term} → {translation}")

    # Save custom glossary to file
    custom_path = Path("/tmp/my_glossary.json")
    glossary.save_glossary(str(custom_path), "react_custom")
    print(f"\n💾 Glossary saved to: {custom_path}")

    # Create translator with custom glossary
    print(f"\n🤖 Creating translator with custom glossary...")
    translator = DocumentTranslator(
        glossary_path=str(custom_path),
        quality_threshold=0.8
    )

    # Test translation with custom glossary
    test_text = "React components use state and props for rendering"

    print(f"\n📝 Test Translation:")
    print("-" * 50)
    print(f"Original: {test_text}")

    # Get glossary context
    hints = translator.translator.get_translation_quality_hints(test_text)
    print(f"\nQuality Hints:")
    print(f"  Technical Terms Found: {len(hints['technical_terms'])}")
    for term, translation in hints['technical_terms'][:5]:
        print(f"    - {term} → {translation}")

    # Merge glossaries
    print(f"\n🔗 Merging glossaries...")
    if glossary.merge_glossaries("tech", "react_custom", overwrite=False):
        print(f"✅ Merged react_custom into tech glossary")
        merged_size = glossary.get_glossary_size("tech")
        print(f"   Tech glossary now has {merged_size.get('tech', 0)} terms")

    print(f"\n✨ Example completed!")


if __name__ == "__main__":
    main()
