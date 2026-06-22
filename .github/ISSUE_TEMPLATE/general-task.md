---
name: General Development Task
about: Standard template for development tasks with testing and workflow requirements
title: '[TASK] '
labels: ['enhancement']
assignees: []
---

## Task Description

**Brief Summary:**
<!-- Clearly describe what needs to be done -->

**Motivation:**
<!-- Why is this task needed? What problem does it solve? -->

## Implementation Requirements

### Core Changes

- [ ] <!-- List specific changes needed -->
- [ ] <!-- Be precise about what files/functions to modify -->
- [ ] <!-- Include any new files that need to be created -->

### Code Quality Standards

- [ ] Follow existing code patterns and naming conventions
- [ ] Add comprehensive docstrings and type hints
- [ ] Ensure all functions have proper error handling
- [ ] Use descriptive variable and function names
- [ ] Follow the project's architectural patterns

## Testing Requirements

### Unit Tests (MANDATORY)

- [ ] Create/update unit tests for all new functionality
- [ ] Test both success and failure scenarios
- [ ] Add edge case testing (empty inputs, boundary values, etc.)
- [ ] Use appropriate test fixtures and mocking

### Integration Tests

- [ ] Test integration with existing components
- [ ] Test real device scenarios if applicable
- [ ] Validate registry validation tests pass

### Test Execution Checklist

- [ ] Run: `python -m pytest tests/ -v`
- [ ] All tests must pass with 0 failures
- [ ] No test warnings or deprecation notices

## Code Quality Validation

### Script-Based Formatting and Linting (MANDATORY)

**CRITICAL: These commands MUST be run after implementation and ALL issues fixed:**

- [ ] Run: `./scripts/format.sh --fix` (fix all formatting issues)
- [ ] Run: `./scripts/format.sh --check` (verify formatting is correct)
- [ ] Run: `./scripts/lint.sh --all` (run all linting checks — ruff, mypy, shellcheck)
- [ ] **Zero violations allowed in any linting tool**

## GitHub Workflow Compliance

### CI/CD Requirements (MANDATORY)

- [ ] All GitHub Actions workflows must pass
- [ ] Pull request checks must be green
- [ ] No failing status checks allowed
- [ ] Branch is up-to-date with main before merging

### Pre-commit Validation

Before creating pull request, run these commands:

```bash
# Activate virtual environment
source .venv/bin/activate

# MANDATORY: Format and validate code using scripts
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all

# Run comprehensive tests
python -m pytest tests/ -v

# Manual validation
python -c "import bluetooth_sig; print('Import successful')"
```

**CRITICAL: All format and lint scripts must pass with zero issues before creating pull request.**

## Files to Modify/Create

### Expected File Changes

- [ ] `src/bluetooth_sig/...` <!-- List specific files -->
- [ ] `tests/...` <!-- List test files -->
- [ ] Update relevant `__init__.py` files for new modules
- [ ] Update documentation if needed

### Registry Updates (if applicable)

- [ ] Regenerate lazy exports if GATT modules added: `python scripts/generate_lazy_exports.py`
- [ ] Ensure proper registration in respective registries

## Definition of Done

### Functional Requirements

- [ ] All specified functionality is implemented
- [ ] Code follows project architectural patterns
- [ ] No breaking changes to existing functionality

### Quality Gate (ALL MUST PASS)

- [ ] **Script-based format check passes: `./scripts/format.sh --check`**
- [ ] **Script-based lint check passes: `./scripts/lint.sh --all`**
- [ ] **All tests pass: 0 failures**
- [ ] **All GitHub workflows pass**
- [ ] **No import errors or syntax issues**

### Documentation

- [ ] Add/update docstrings for all new functions/classes
- [ ] Update relevant documentation files if needed
- [ ] Include usage examples in docstrings
- [ ] Document any new configuration options

## Related Information

**Dependencies:**
<!-- List any dependencies on other issues or external factors -->

**References:**

- [Bluetooth SIG Assigned Numbers](https://www.bluetooth.com/specifications/assigned-numbers/)
- [GATT Services & Characteristics Specifications](https://www.bluetooth.com/specifications/specs/)
- Local YAML Registry Files:
  - Services: `bluetooth_sig/assigned_numbers/uuids/service_uuids.yaml`
  - Characteristics: `bluetooth_sig/assigned_numbers/uuids/characteristic_uuids.yaml`
  - Specifications: `bluetooth_sig/gss/org.bluetooth.characteristic.*.yaml`

**Breaking Changes:**
<!-- Note if this introduces any breaking changes -->

## Success Criteria

**The task is complete when:**

1. All implementation requirements are met
2. All tests pass with 100% success rate
3. **MANDATORY: `./scripts/format.sh --check` passes with zero issues**
4. **MANDATORY: `./scripts/lint.sh --all` passes with zero issues**
5. All GitHub workflows are green
6. Code is properly documented and follows project patterns
7. No regressions in existing functionality

**Note for Copilot:**

- **MANDATORY**: Run `./scripts/format.sh --fix` and `./scripts/lint.sh --all` after implementation
- **TASK NOT COMPLETE**: Until all script-based quality checks pass with zero issues
- Follow the bluetooth-sig library's existing patterns and architecture
- Use the bluetooth_sig submodule for UUID lookups (check YAML files above)
- Ensure all characteristics implement proper decode/encode methods with appropriate data types
- Test against real device scenarios when possible
- Maintain backward compatibility with existing implementations
- Reference Bluetooth SIG specifications for data formats and units
