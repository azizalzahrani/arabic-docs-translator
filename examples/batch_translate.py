#!/usr/bin/env python3
"""
مثال: ترجمة دفعية
Example: Batch Translation.

يوضح كيفية ترجمة مجلد كامل من الملفات
Demonstrates how to batch translate an entire folder.
"""

from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arabic_translator import BatchTranslator


def create_sample_docs():
    """إنشاء ملفات عينة للاختبار"""
    sample_dir = Path("/tmp/sample_docs")
    sample_dir.mkdir(exist_ok=True)

    # Sample file 1
    with open(sample_dir / "readme.md", "w", encoding="utf-8") as f:
        f.write("""# Getting Started

Welcome to our documentation. This guide will help you get started quickly.

## Installation

```bash
npm install my-package
```

## Basic Usage

Import the package and start using it:

```javascript
import MyPackage from 'my-package';

const instance = new MyPackage();
```
""")

    # Sample file 2
    with open(sample_dir / "api.md", "w", encoding="utf-8") as f:
        f.write("""# API Reference

This document describes the available API endpoints.

## GET /users

Returns a list of all users.

**Response:**
```json
{
  "users": [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
  ]
}
```

## POST /users

Create a new user.

**Request Body:**
- `name` (string): User's name
- `email` (string): User's email
""")

    return sample_dir


def main():
    """الدالة الرئيسية"""
    # Create sample documents
    input_folder = create_sample_docs()
    output_folder = Path("/tmp/translated_docs")

    print("🚀 Starting Batch Translation")
    print(f"📁 Input Folder: {input_folder}")
    print(f"📁 Output Folder: {output_folder}")
    print("-" * 50)

    # Initialize batch translator
    batch_translator = BatchTranslator(
        num_workers=2,
        quality_threshold=0.8
    )

    # Translate folder
    results = batch_translator.translate_folder(
        str(input_folder),
        str(output_folder),
        file_pattern="*.md",
        recursive=True
    )

    # Display results
    print(f"\n📊 Translation Results:")
    print("-" * 50)

    for file_path, result in results.items():
        status = result.get('status', 'unknown')
        quality = result.get('quality_score', 0)

        if status == 'success':
            print(f"✅ {file_path}")
            print(f"   Quality: {quality:.2%}")
            print(f"   Output: {result.get('output_path')}")
        else:
            print(f"❌ {file_path}")
            if 'error' in result:
                print(f"   Error: {result['error']}")

    # Summary
    summary = batch_translator.get_batch_summary(results)

    print(f"\n📈 Batch Summary:")
    print("-" * 50)
    print(f"Total Files: {summary['total_files']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    print(f"Average Quality Score: {summary['average_quality_score']:.2%}")
    print(f"High Quality Files: {summary['high_quality_files']}")

    # List output files
    print(f"\n📂 Translated Files:")
    print("-" * 50)
    for file in sorted(Path(output_folder).rglob("*.md")):
        print(f"  - {file.relative_to(output_folder)}")


if __name__ == "__main__":
    main()
