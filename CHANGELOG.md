# Changelog

## 0.2.0 - 2026-06-12

### Fixed
- `translate_with_review()` / CLI `--review` crashed with `TypeError` (`len()` of an `int`) in the reviewer's code-fence check.
- Adapter stripped hamzas (`أ → ا`, `ؤ → و`, `ئ → ي`), corrupting correct Arabic orthography in every output.
- Adapter rewrote URLs, numbers, and inline code: `https://x.com` became `بروتوكول نقل النص الفائق الآمن://x.com`, `1,000` became `1،000`. Punctuation conversion is now context-aware (Arabic-adjacent only) and code/links/placeholders are shielded.
- Adapter collapsed all newlines, merging multi-line blockquotes and paragraphs into one line.
- Markdown round-trip dropped code-fence language tags (` ```python ` became ` ``` `).
- Ordered lists (`1.` / `1)`) were silently skipped during translation.
- Quality scorer divided glossary matches by *all* long words instead of glossary-known words, deflating every score.
- Custom glossaries could not override built-in terms (lookup priority is now custom → framework → tech).
- `setup.py` pointed to the wrong repository URL.
- YAML frontmatter was parsed as content; it is now preserved verbatim.

### Added
- Live LLM provider layer (`arabic_translator/providers.py`): OpenAI and Anthropic integrations with retry on transient errors, lazy SDK imports, and env-based auto-detection.
- Safe **dry-run mode** when no API key is configured: structure is processed, text is returned untranslated, and a warning is printed (previously every paragraph was replaced with a placeholder string).
- CLI flags: `--provider {auto,openai,anthropic,none}` and `--workers N`.
- Parallel batch translation via thread pool (`num_workers` was previously ignored).
- Guard against re-translating the output folder when it nests inside the input folder.
- Measured `translation_time` and `dry_run` flag in results.
- GitHub Actions CI (pytest on Python 3.9 / 3.11 / 3.12).
- 32 new tests (agents, providers, end-to-end pipeline).

### Changed
- Runtime dependencies trimmed to `python-dotenv` + `pydantic`; provider SDKs are optional extras (`.[openai]`, `.[anthropic]`, `.[all]`); dev tools moved to `.[dev]` / `requirements-dev.txt`.
- Default model is now `auto` (provider default, overridable via env or `--model`) instead of hard-coded `gpt-4`.
- Translation prompts harden placeholder/inline-code/link preservation and request output-only replies.
- `MarkdownParser.extract_text_elements()` returns a plain `list` (the substring-membership wrapper class was removed); ordered list items are now included.
