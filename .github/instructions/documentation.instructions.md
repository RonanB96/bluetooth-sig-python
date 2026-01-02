---
applyTo: "docs/**/*.md, docs/*.md"
---

# Documentation Authoring Guidelines

## Naming and Terminology (Authoritative)
 - Use consistent API vocabulary that mirrors the public surface (`BluetoothSIGTranslator.parse_characteristic`, `CharacteristicData.value`, etc.). Follow project naming conventions and PEP 8 for consistent, intuitive names.
 - Prefer nouns for section titles and task-oriented headings (for example, "Parse Characteristics" instead of "Parsing Characteristics") to improve discoverability and consistency.
- When explaining BLE concepts, introduce the SIG term first, then the library abstraction (e.g., "Battery Level characteristic (`2A19`) → `CharacteristicName.BATTERY_LEVEL`").

## Code Sample Requirements
- Every code block must be copy-paste runnable and import from `bluetooth_sig` using the public re-exports unless there is a documented reason otherwise.
- Validate snippets before publishing; examples that fail at runtime (missing methods, stale names) are unacceptable and must be executed/verified before inclusion.
- Pair code with its expected output or a short assertion so readers can self-verify results.
- Highlight context-dependent snippets with prerequisites (environment variables, BLE connection managers, etc.) directly above the block.
- **Use Sphinx cross-references** for all Python objects: `:class:`bluetooth_sig.SomeClass``, `:meth:`bluetooth_sig.SomeClass.method``, `:func:`bluetooth_sig.some_function``
- For objects in the public API, use: `:class:`CharacteristicData``, `:class:`BaseCharacteristic``, etc.
- Method references: `:meth:`BluetoothSIGTranslator.parse_characteristic``
- **Link context near code blocks**: Add prose with cross-references before/after code blocks to provide context
- Example pattern: "The :meth:`parse_characteristic` method returns a :class:`CharacteristicData` object:" followed by the code block

## Python-specific API & Documentation References


- Official Python language & documentation guidance:
  - PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
  - PEP 484 — Type Hints: https://peps.python.org/pep-0484/
  - Python standard library documentation: https://docs.python.org/3/

 - Docstrings & in-code documentation:
   - Detailed, code-level docstring guidance (PEP 257 conventions, preferred docstring style, enforcement and doctest examples) has been moved to `.github/instructions/python-implementation.instructions.md` — that file is the authoritative source for in-code documentation rules for Python files.

- Doc generation toolchain:
  - Sphinx (used by this project): https://www.sphinx-doc.org/
  - Sphinx autodoc + napoleon for Google-style docstrings: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html and https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
  - Read the Docs (hosting): https://docs.readthedocs.io/

- Packaging & distribution:
  - Python Packaging Authority (packaging guide): https://packaging.python.org/

These Python-focused references inform the following recommendations for documentation maintainers.

- Use PEP 8 and PEP 484 as the coding and typing baseline for Python code.
- Keep user-facing documentation (how-to, guides, examples) in the `docs/` folder — the docs site is the primary home for narrative content.
- Docstring style (canonical): Google style is the project's canonical in-code docstring format. See `.github/instructions/python-implementation.instructions.md` for the project’s detailed, enforceable rules on docstring structure, examples and CI enforcement.

## Structural Expectations
- Start each page with a one-sentence summary followed by bullets that outline what the reader will gain; keep paragraphs under three sentences for scannability.
- Use ordered lists for procedural steps and unordered lists for options or feature highlights.
- **Use Sphinx cross-references** throughout all documentation for Python objects
  - Classes: `:class:`bluetooth_sig.BluetoothSIGTranslator``
  - Methods: `:meth:`BluetoothSIGTranslator.parse_characteristic``
  - Functions: `:func:`bluetooth_sig.some_function``
  - Modules: `:mod:`bluetooth_sig.gatt``
- Cross-reference related content using Sphinx roles so autodoc generates proper hyperlinks automatically
- Use `:ref:` for internal section links and `:doc:` for linking to other documentation pages.

## Style and Voice
- Write in active voice with second-person guidance ("You can", "Configure", "Call") to match the conversational tone in the Quick Start.
- Explain new terms the first time they appear; if a SIG acronym is required, expand it and link to the official spec when possible.
- Avoid future tense promises; describe current behaviour the library already implements.

## Visuals and Tables
- Prefer markdown tables for capability matrices; keep column headers concise and align numerical data to the right for readability.
- When embedding diagrams, add descriptive alt text and store assets under `docs/images/`.

## Review Checklist
- [ ] Names and method references match the current API implementation.
- [ ] Examples were executed locally (or via tests) and output was confirmed.
- [ ] Links are relative and resolve within the docs build.
- [ ] Page summary and section headings follow the noun-based convention.
- [ ] Terminology aligns with SIG specifications and library enums.
