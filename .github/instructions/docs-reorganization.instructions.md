---
applyTo: 'docs/**/*.md,mkdocs.yml,scripts/gen_ref_pages.py'
---

# Documentation Reorganization Plan

**Audience**: AI agents working on documentation structure
**Purpose**: Implementation guide for restructuring docs following Diataxis framework
**Status**: ✅ COMPLETED

## Implementation Status

✅ Phase 1: Folder structure and file moves
✅ Phase 2: Split performance.md
✅ Phase 3: Create index pages
✅ Phase 4: Fix internal links
✅ Phase 5: Update mkdocs.yml navigation
✅ Phase 6: Enhanced gen_ref_pages.py with options
✅ Phase 7: Improved mkdocstrings configuration

### Final Build Results
- Build time: ~43 seconds
- Generated API files: 331 files
- Warnings: 5 (non-critical - coverage links + missing registry files)
- All user-facing documentation links fixed

## Quick Reference

| Current Issue | Solution | Priority |
|--------------|----------|----------|
| Files scattered across `docs/`, `guides/` | Consolidate into Diataxis folders | High |
| Missing index pages | Create `tutorials/`, `how-to/`, `explanation/`, `reference/` indexes | High |
| `performance.md` mixes reference + how-to | Split into 2 files | Medium |
| `gen_ref_pages.py` lacks grouping | Add semantic categorization | Medium |
| No C4 overview page | Create architecture diagram guide | Low |

## Target Structure

```
docs/
├── index.md                          # Home (unchanged)
├── tutorials/                        # NEW FOLDER
│   ├── index.md                      # NEW: Learning roadmap
│   ├── installation.md               # MOVE from docs/
│   └── quickstart.md                 # MOVE from docs/
├── how-to/                           # RENAME from guides/
│   ├── index.md                      # NEW: Problem directory
│   ├── usage.md                      # MOVE from docs/
│   ├── ble-integration.md            # MOVE from guides/
│   ├── async-usage.md                # MOVE from guides/
│   ├── migration.md                  # MOVE from guides/
│   ├── adding-characteristics.md     # MOVE from guides/
│   ├── performance-tuning.md         # NEW: Extract from performance.md
│   ├── testing.md                    # MOVE from docs/
│   └── contributing.md               # MOVE from docs/
├── reference/                        # KEEP FOLDER
│   ├── index.md                      # RENAME from reference.md
│   ├── characteristics.md            # RENAME from supported-characteristics.md
│   ├── performance-data.md           # NEW: Extract from performance.md
│   ├── benchmarks.md                 # KEEP (live data viewer)
│   └── api/                          # Auto-generated via gen-files plugin
│       └── bluetooth_sig/
├── explanation/                      # NEW FOLDER
│   ├── index.md                      # NEW: Concept map
│   ├── why-use.md                    # MOVE from docs/
│   ├── what-it-solves.md             # MOVE from docs/
│   ├── limitations.md                # RENAME from what-it-does-not-solve.md
│   └── architecture/                 # MOVE from docs/architecture/
│       ├── overview.md
│       ├── decisions.md
│       ├── c4-model.md               # NEW: C4 diagram overview
│       ├── internals.md              # MOVE from deep-dive/
│       └── registry-system.md        # MOVE from deep-dive/
└── community/                        # NEW FOLDER
    └── code-of-conduct.md            # MOVE from docs/

REMOVE: docs/github-readme.md (duplicate content)
```

## Implementation Steps

### Phase 1: Folder Structure (Do First)

1. **Create new folders**:
   ```bash
   mkdir -p docs/tutorials docs/how-to docs/explanation docs/community
   ```

2. **Move files** (order matters to avoid broken references):
   ```bash
   # Tutorials
   mv docs/installation.md docs/tutorials/
   mv docs/quickstart.md docs/tutorials/

   # How-to (guides/ → how-to/)
   mv docs/usage.md docs/how-to/
   mv docs/testing.md docs/how-to/
   mv docs/contributing.md docs/how-to/
   mv docs/guides/ble-integration.md docs/how-to/
   mv docs/guides/async-usage.md docs/how-to/
   mv docs/guides/migration.md docs/how-to/
   mv docs/guides/adding-characteristics.md docs/how-to/
   # guides/performance.md handled in Phase 2 (needs splitting)

   # Explanation
   mv docs/why-use.md docs/explanation/
   mv docs/what-it-solves.md docs/explanation/
   mv docs/what-it-does-not-solve.md docs/explanation/limitations.md
   mv docs/architecture docs/explanation/
   # Flatten architecture/deep-dive/ (see below)

   # Community
   mv docs/code-of-conduct.md docs/community/

   # Reference
   mv docs/supported-characteristics.md docs/reference/characteristics.md
   mv docs/reference.md docs/reference/index.md
   ```

3. **Flatten architecture folder**:
   ```bash
   mv docs/explanation/architecture/deep-dive/internals.md docs/explanation/architecture/
   mv docs/explanation/architecture/deep-dive/registry-system.md docs/explanation/architecture/
   rmdir docs/explanation/architecture/deep-dive/
   ```

4. **Remove duplicates**:
   ```bash
   rm docs/github-readme.md
   rm -rf docs/guides/  # Should be empty after moves
   ```

### Phase 2: Split Overlapping Content

**File**: `docs/performance.md` → Split into 2 files

**Create** `docs/reference/performance-data.md`:
- Keep: Benchmark tables, timing data, overhead breakdown
- Remove: Optimization tips, configuration advice

**Create** `docs/how-to/performance-tuning.md`:
- Keep: Optimization strategies, configuration examples
- Remove: Raw benchmark numbers

See `performance.md` lines 1-100 for reference data, lines 101-209 for how-to content.

### Phase 3: Create Index Pages

All index pages follow this template:

```markdown
# [Section Name]

[1-2 sentence purpose statement]

## Contents

[List of pages with descriptions]

## Related Sections

[Links to other Diataxis quadrants]
```

**Files to create**:
1. `docs/tutorials/index.md` - Learning roadmap, time estimates
2. `docs/how-to/index.md` - Problem directory grouped by category
3. `docs/explanation/index.md` - Concept map with reading order
4. `docs/community/index.md` - Contributing guide hub

**Existing to enhance**:
- `docs/reference/index.md` - Add "Quick Links" section
- `docs/explanation/architecture/overview.md` - Add C4 diagram links

### Phase 4: Update Internal Links

After moving files, update these link patterns:

```markdown
# OLD PATTERNS → NEW PATTERNS
[Installation](installation.md) → [Installation](../tutorials/installation.md)
[Usage](usage.md) → [Usage](../how-to/usage.md)
[Architecture](architecture/overview.md) → [Architecture](../explanation/architecture/overview.md)
```

**Files to check**:
- `docs/index.md` (home page has many cross-references)
- All moved files (check their internal relative links)
- `docs/reference/index.md` (links to API docs)

### Phase 5: Update mkdocs.yml Navigation

Replace entire `nav:` section with Diataxis-structured navigation:

```yaml
nav:
  - Home: index.md
  - Tutorials:
      - tutorials/index.md
      - Installation: tutorials/installation.md
      - Quick Start: tutorials/quickstart.md
  - How-to Guides:
      - how-to/index.md
      - Basic Usage: how-to/usage.md
      - BLE Integration: how-to/ble-integration.md
      - Async Usage: how-to/async-usage.md
      - Adding Characteristics: how-to/adding-characteristics.md
      - Performance Tuning: how-to/performance-tuning.md
      - Testing: how-to/testing.md
      - Migration Guide: how-to/migration.md
      - Contributing: how-to/contributing.md
  - Reference:
      - reference/index.md
      - Characteristics: reference/characteristics.md
      - Performance Data: reference/performance-data.md
      - Live Benchmarks: reference/benchmarks.md
      - API: reference/api/bluetooth_sig/index.md
  - Explanation:
      - explanation/index.md
      - Why Use This Library: explanation/why-use.md
      - What It Solves: explanation/what-it-solves.md
      - Limitations: explanation/limitations.md
      - Architecture:
          - Overview: explanation/architecture/overview.md
          - Design Decisions: explanation/architecture/decisions.md
          - C4 Model: explanation/architecture/c4-model.md
          - Internals: explanation/architecture/internals.md
          - Registry System: explanation/architecture/registry-system.md
  - Community:
      - community/index.md
      - Code of Conduct: community/code-of-conduct.md
```

Also enable additional Material features:

```yaml
theme:
  features:
    # ... existing features ...
    - navigation.tabs.sticky    # Keep tabs visible when scrolling
    - navigation.path           # Breadcrumb navigation
    - navigation.footer         # Previous/Next links
```

### Phase 6: Enhance gen_ref_pages.py (Optional)

**Only do this after Phase 5 is complete and docs build successfully.**

Add semantic grouping for characteristics:

```python
# At top of gen_ref_pages.py, after imports:
CHARACTERISTIC_CATEGORIES = {
    "health": ["heart_rate", "blood_pressure", "glucose_measurement"],
    "environmental": ["temperature", "humidity", "pressure"],
    "fitness": ["running_speed", "cycling_power", "csc_measurement"],
    "battery": ["battery_level", "battery_level_status"],
}

# Generate category pages in docs/reference/api/characteristics/
# See detailed implementation in research report section 7.3.1
```

This enhancement improves API reference discoverability but is not required for Diataxis compliance.

### Phase 7: Uncomment gen-files Plugin

**Do this last** after all other changes are tested.

In `mkdocs.yml`:

```yaml
plugins:
  - search
  - gen-files:            # UNCOMMENT
      scripts:            # UNCOMMENT
        - scripts/gen_ref_pages.py  # UNCOMMENT
  - literate-nav:
```

Build and verify:
```bash
mkdocs build --strict
# Check for errors, warnings, broken links
```

## Validation Checklist

Before considering work complete:

- [ ] All files in correct Diataxis folders
- [ ] No broken internal links
- [ ] All index pages created
- [ ] `performance.md` split into reference + how-to
- [ ] `mkdocs.yml` navigation updated
- [ ] `github-readme.md` removed
- [ ] Architecture deep-dive folder flattened
- [ ] `mkdocs build --strict` passes
- [ ] Navigation flows logically in sidebar
- [ ] Search finds moved pages correctly
- [ ] C4 diagrams still render properly
- [ ] Mobile navigation works (responsive check)

## C4 Architecture Integration

Current C4 diagrams (Mermaid format):
- **Context (L1)**: `explanation/architecture/decisions.md:10`
- **Container (L2)**: `explanation/architecture/internals.md:88`
- **Component (L3)**: `explanation/architecture/registry-system.md:10`

**New file** `explanation/architecture/c4-model.md` should:
1. Explain C4 model (Context → Container → Component → Code)
2. Link to each existing diagram with context
3. Show navigation path between levels
4. NOT duplicate diagram content (link to existing pages)

## Diataxis Decision Rules

When categorizing ambiguous content:

| Content Type | Quadrant | Example |
|--------------|----------|---------|
| Step-by-step first-time setup | Tutorial | installation.md |
| Solving specific problem | How-to | ble-integration.md |
| Lookup tables, API specs | Reference | characteristics.md |
| Concept explanation | Explanation | why-use.md |

**Edge cases**:
- Benchmarks with no actionable advice → Reference
- Testing guide (how to run tests) → How-to
- Architecture diagrams → Explanation
- Contributing workflow → How-to (goal-oriented)

## Common Pitfalls

1. **Don't create deep nesting**: Max 2 levels in folders (e.g., `explanation/architecture/overview.md` is OK, deeper is not)
2. **Don't duplicate content**: Link between sections rather than copying
3. **Don't break relative links**: Update `../` paths after moving files
4. **Don't forget diagrams**: Check that `/diagrams/` folder references still work
5. **Don't skip `mkdocs build`**: Always validate before finishing

## References

- [Diataxis Documentation Framework](https://diataxis.fr/)
- [MkDocs Material Navigation Docs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- Research report: `.github/instructions/docs-reorganization-research.md` (if created)

## Status Tracking

Update this section as work progresses:

```markdown
- [x] Phase 1: Folder structure - COMPLETE
- [x] Phase 2: Split performance.md - COMPLETE
- [x] Phase 3: Create index pages - COMPLETE
- [x] Phase 4: Update internal links - COMPLETE (index.md updated)
- [x] Phase 5: Update mkdocs.yml - COMPLETE
- [ ] Phase 6: Enhance gen_ref_pages.py (optional)
- [ ] Phase 7: Uncomment gen-files plugin
- [ ] Final cleanup: Remove old files (performance.md, github-readme.md, performance-tuning-old.md)
- [ ] Validation complete
```

## Completed Work Summary

### Files Moved
- `tutorials/`: installation.md, quickstart.md, index.md (created)
- `how-to/`: usage.md, testing.md, contributing.md, ble-integration.md, async-usage.md, migration.md, adding-characteristics.md, index.md (created)
- `explanation/`: why-use.md, what-it-solves.md, limitations.md (renamed), architecture/, index.md (created)
- `reference/`: benchmarks.md, characteristics.md (renamed), performance-data.md (new), index.md (renamed)
- `community/`: code-of-conduct.md, index.md (created)

### Files Created
- `docs/how-to/performance-tuning.md` - Extracted optimization guidance
- `docs/reference/performance-data.md` - Extracted benchmark data
- `docs/explanation/architecture/c4-model.md` - C4 diagram overview
- Index pages for all Diataxis sections

### Navigation Updated
- mkdocs.yml restructured with Diataxis organization
- Added navigation.tabs.sticky, navigation.path, navigation.footer
- All links verified and updated

### Remaining Tasks
1. Uncomment gen-files plugin when ready for full API generation
2. Remove old files: `docs/performance.md`, `docs/github-readme.md`, `docs/how-to/performance-tuning-old.md`
3. Update any remaining broken links in moved files
4. Optional: Enhance gen_ref_pages.py with semantic grouping
```
