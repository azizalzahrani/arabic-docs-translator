#!/usr/bin/env python3
"""
مثال: ترجمة ملف Markdown
Example: Translate a Markdown file.

يوضح كيفية ترجمة ملف Markdown واحد
Demonstrates how to translate a single Markdown file.
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arabic_translator import DocumentTranslator


def main():
    """الدالة الرئيسية"""
    # Initialize translator
    translator = DocumentTranslator(
        quality_threshold=0.8,
        model="gpt-4"
    )

    # Example markdown content
    example_md = """
# React Hooks Guide

React Hooks allow you to use state and other React features without writing a class component.

## useState Hook

The `useState` hook lets you add state to functional components.

```javascript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

## useEffect Hook

The `useEffect` hook lets you perform side effects in functional components.

- Runs after every render
- Can return a cleanup function
- Can specify dependencies array

## Best Practices

1. Only call hooks at the top level
2. Don't call hooks inside loops or conditions
3. Use the ESLint plugin to enforce these rules
    """

    # Create temporary input file
    input_file = Path("/tmp/example.md")
    output_file = Path("/tmp/example_ar.md")

    with open(input_file, "w", encoding="utf-8") as f:
        f.write(example_md)

    print("📄 Translating Markdown file...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print("-" * 50)

    # Translate file
    result = translator.translate_file(
        str(input_file),
        str(output_file)
    )

    # Display results
    print(f"\n✅ Translation Status: {result['status']}")
    print(f"📊 Quality Score: {result['quality_score']:.2%}")
    print(f"✓ Quality Passed: {result['quality_passed']}")
    print(f"📁 Output: {result['output_path']}")

    # Show quality details
    if 'quality_report' in result:
        report = result['quality_report']
        print(f"\n📈 Quality Breakdown:")
        for metric, score in report['scores_breakdown'].items():
            print(f"  - {metric}: {score:.2%}")

    # Read and display translated content
    with open(output_file, "r", encoding="utf-8") as f:
        translated = f.read()

    print(f"\n🌍 Translated Content (first 500 chars):")
    print("-" * 50)
    print(translated[:500])
    print("...")


if __name__ == "__main__":
    main()
