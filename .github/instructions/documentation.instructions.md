---
applyTo: "docs/**/*.md, docs/*.md, mkdocs.yml"
---

# Documentation Authoring Guidelines

## Naming and Terminology (Authoritative)
- Use consistent API vocabulary that mirrors the public surface (`BluetoothSIGTranslator.parse_characteristic`, `CharacteristicData.value`, etc.). This aligns with Google API naming guidance on intuitive, uniform terms (https://cloud.google.com/apis/design/naming_convention).
- Prefer nouns for section titles and task-oriented headings (for example, "Parse Characteristics" instead of "Parsing Characteristics"), matching Microsoft REST documentation best practices for discoverability: https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design
- When explaining BLE concepts, introduce the SIG term first, then the library abstraction (e.g., "Battery Level characteristic (`2A19`) → `CharacteristicName.BATTERY_LEVEL`").

## Code Sample Requirements
- Every code block must be copy-paste runnable and import from `bluetooth_sig` using the public re-exports unless there is a documented reason otherwise.
- Validate snippets before publishing; examples that fail at runtime (missing methods, stale names) are not acceptable per Swagger/OpenAPI documentation accuracy guidance (https://swagger.io/resources/articles/documenting-apis-with-swagger/).
- Pair code with its expected output or a short assertion so readers can self-verify results.
- Highlight context-dependent snippets with prerequisites (environment variables, BLE connection managers, etc.) directly above the block.
- **Use mkdocstrings automatic cross-references** for all Python objects: `[text][full.path.to.object]` or `[full.path.to.object][]`
- For objects in the public API, use: `[CharacteristicData][]`, `[BaseCharacteristic][]`, etc.
- Method references: `[parse_characteristic][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic]`
- **Link context near code blocks**: Since mkdocstrings doesn't auto-link inside regular code examples, add prose with links before/after code blocks to provide context
- Example pattern: "The [parse_characteristic][] method returns a [CharacteristicData][] object:" followed by the code block
- Enable `signature_crossrefs` in mkdocs.yml for automatic linking in API method signatures

## Structural Expectations
- Start each page with a one-sentence summary followed by bullets that outline what the reader will gain; keep paragraphs under three sentences for scannability.
- Use ordered lists for procedural steps and unordered lists for options or feature highlights.
- **Use mkdocstrings automatic cross-references** throughout all documentation for Python objects
  - Syntax: `[text][full.path.to.object]` or `[full.path.to.object][]` for automatic title
  - Public API objects: `[BluetoothSIGTranslator][]` automatically links to the generated API docs
  - Methods: `[parse_characteristic][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic]`
  - Types: `[CharacteristicData][]` links to the dataclass documentation
- Cross-reference related content using these auto-links so mkdocstrings generates proper hyperlinks automatically
- MkDocs anchor links (e.g., `api/types.md#characteristicdata`) should only be used for section headings, not for API objects

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
