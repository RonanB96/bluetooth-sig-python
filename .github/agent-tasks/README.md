# Agent Tasks - Quick Reference

This document provides a quick overview of all available agent tasks for improving the Bluetooth SIG Standards Library.

## 📖 Essential Reading

**[Bluetooth SIG to Library Mapping](../SIG-MAPPING.md)** - Understand how our library directly maps to official Bluetooth SIG specifications. This document shows:
- How SIG components (Appearance Values, Company IDs, etc.) map to library modules
- Why tasks 04-08 are critical for user experience
- The design principle: users should never need to understand YAML parsing or threading

## Task Matrix

| ID | Task | Priority | Effort | Dependencies | Status |
|----|------|----------|--------|--------------|--------|
| 01 | [Context Support for Health Characteristics](01-context-support-health-characteristics.md) | P1 | Medium | None | 🟢 Complete |
| 02 | [Improve Test Coverage](02-improve-test-coverage.md) | P1 | Medium | None | 🔴 Not Started |
| 03 | [Performance Benchmarking Suite](03-performance-benchmarking.md) | P1 | Medium | None | 🔴 Not Started |
| 04 | [Company Identifiers Registry](04-company-identifiers-registry.md) | P1 | Low | Task 20 | 🔴 Not Started |
| 05 | [Appearance Values Registry](05-appearance-values-registry.md) | P1 | Medium | Task 20 | 🔴 Not Started |
| 06 | [AD Types Registry](06-ad-types-registry.md) | P1 | Low | Task 20 | 🔴 Not Started |
| 07 | [Class of Device Registry](07-class-of-device-registry.md) | P2 | Medium | Task 20 | 🔴 Not Started |
| 08 | [Protocol Identifiers Registry](08-protocol-identifiers-registry.md) | P2 | Low | Task 20 | 🔴 Not Started |
| 09 | Property-Based Testing | P2 | Medium | Task 02 | 📝 Not Created |
| 10 | Descriptor Support Enhancement | P2 | Medium | None | 📝 Not Created |
| 11 | [Async API Variants](11-async-api-variants.md) | P1 | Medium-High | None | 🟢 Complete |
| 12 | Service-Level Validation | P2 | Medium | Task 16 | 📝 Not Created |
| 13 | [Tutorial Documentation](13-tutorial-documentation.md) | P1 | Medium | Task 01 | 🔴 Not Started |
| 14 | Cookbook Recipes | P2 | Medium | Task 13 | 📝 Not Created |
| 15 | API Usage Patterns | P2 | Low-Medium | Task 11 | ➖ Not Needed (covered by docs/usage.md) |
| 16 | Missing Services Implementation | P2 | High | None | 📝 Not Created |
| 17 | Missing Characteristics | P3 | Very High | Task 16 | 📝 Not Created |
| 18 | CLI Tool | P3 | Medium | Tasks 03, 11 | 📝 Not Created |
| 19 | Plugin System | P3 | High | Tasks 16, 17 | 📝 Not Created |
| 20 | [Restructure Registry to Mirror SIG](20-restructure-registry-mirror-sig.md) | P0 | Medium | None | 🔴 **DO FIRST** |
| 17 | Missing Characteristics | P3 | Very High | Task 16 | 📝 Not Created |
| 18 | CLI Tool | P3 | Medium | Tasks 03, 11 | 📝 Not Created |
| 19 | Plugin System | P3 | High | Tasks 16, 17 | 📝 Not Created |

**Legend**:
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 📝 Not Created Yet
- ➖ Not Needed / No Longer Relevant

## Critical Path for v0.4.0

**Phase 0** (Week 0): **RESTRUCTURE FIRST** 🚨
```
20 (Restructure Registry) ← DO THIS BEFORE ALL OTHER REGISTRY TASKS
```

**Phase 1** (Week 1-2): Core Improvements
```
01 (Context) ✅ → 02 (Coverage) → 03 (Benchmarks)
```

**Phase 2** (Week 3-4): Registry System (High User Value)
```
04 (Company IDs) → 05 (Appearance) → 06 (AD Types)
```

**Phase 3** (Week 5-6): API & Docs
```
11 (Async) ✅ → 13 (Tutorials)
```

**Phase 4** (Week 7-8): Polish
```
07 (Class of Device) → 08 (Protocols) → 09 (Property Testing) → 10 (Descriptors)
```

## Quick Start for Agents

### First Time?
1. Read [00-INDEX.md](00-INDEX.md) for overview
2. Read [SIG-MAPPING.md](../SIG-MAPPING.md) to understand architecture
3. **Start with Task 20** (Restructure Registry) if working on registries
4. Then tackle registry tasks 04-08

### Experienced?
- 🚨 **Task 20 MUST be done before Tasks 04-08** (restructure registry to mirror SIG)
- Pick any P1 task based on your interests after that

### I want to...

**...restructure for clarity** → Task 20 🚨 **DO THIS FIRST**
**...add missing registries** → Tasks 04-08 (after Task 20) ⭐ HIGH VALUE
**...fix bugs and technical debt** → Task 01 ✅ Complete
**...improve quality** → Task 02
**...measure performance** → Task 03
**...add async support** → Task 11 ✅ Complete
**...improve documentation** → Task 13
**...add advanced testing** → Task 09
**...enhance descriptors** → Task 10
**...add more characteristics** → Tasks 16, 17
**...build tooling** → Tasks 18, 19
**...improve documentation** → Task 08
**...add advanced testing** → Task 04
**...enhance descriptors** → Task 05
**...add more characteristics** → Task 11, 12
**...build tooling** → Task 13, 14

## Estimated Timeline

### Aggressive (8 weeks)
- **Weeks 1-2**: Tasks 01, 02, 03
- **Weeks 3-4**: Tasks 06, 08
- **Weeks 5-6**: Tasks 04, 05
- **Weeks 7-8**: Polish & release v0.4.0

### Realistic (12 weeks)
- **Weeks 1-3**: Tasks 01, 02, 03
- **Weeks 4-6**: Tasks 06, 08
- **Weeks 7-9**: Tasks 04, 05, 09
- **Weeks 10-12**: Tasks 07, 11, Polish & release v0.4.0

### Relaxed (16 weeks)
- **Weeks 1-4**: Tasks 01, 02, 03
- **Weeks 5-8**: Tasks 06, 08
- **Weeks 9-12**: Tasks 04, 05, 09, 10
- **Weeks 13-16**: Tasks 07, 11, Polish & release v0.4.0

## Success Metrics

Track these metrics as tasks are completed:

| Metric | Current | Target (v0.4.0) |
|--------|---------|-----------------|
| Test Coverage | 86% | ≥90% |
| Characteristics | 73 | 80+ |
| Services | 17 | 25+ |
| TODO Comments | 4 | 0 |
| Documentation Pages | ~15 | 25+ |
| Performance Baseline | None | Documented |
| Async Support | No | Yes |

## Communication

### Commit Messages
Format: `[Task-XX] Description`

Examples:
- `[Task-01] Add context support for heart rate measurement`
- `[Task-02] Increase RSSI utils test coverage to 85%`
- `[Task-03] Add performance benchmarking suite`

### Pull Requests
- Reference task file in PR description
- Check off completed acceptance criteria
- Link related issues

### Issues
- Tag with `agent-task` label
- Reference task number
- Cross-reference with task file

## Resources

### Documentation
- [Project README](../../README.md)
- [Architecture Guide](../../docs/architecture/index.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Agent Guidelines](../../AGENTS.md)

### Specifications
- [Bluetooth SIG Specifications](https://www.bluetooth.com/specifications/)
- [Assigned Numbers](https://www.bluetooth.com/specifications/assigned-numbers/)

### Tools
- **Testing**: `python -m pytest tests/ -v`
- **Coverage**: `python -m pytest tests/ --cov=src/bluetooth_sig --cov-report=html`
- **Linting**: `./scripts/lint.sh --all`
- **Formatting**: `./scripts/format.sh --check`
- **Type Checking**: `mypy src/`

## Quality Gates

Before marking any task complete, ensure:

1. ✅ All acceptance criteria met
2. ✅ Tests pass: `python -m pytest tests/ -v`
3. ✅ Coverage maintained or improved
4. ✅ Linting passes: `./scripts/lint.sh --all`
5. ✅ Formatting correct: `./scripts/format.sh --check`
6. ✅ Type hints complete: `mypy src/`
7. ✅ Documentation updated
8. ✅ Examples work (if applicable)

## Getting Help

- **Questions**: Open GitHub issue with `question` label
- **Clarifications**: Comment on task file in PR
- **Bugs**: Open GitHub issue with `bug` label
- **Spec Ambiguities**: Consult Bluetooth SIG docs first, then ask

## Notes

- Tasks are intentionally detailed to reduce ambiguity
- Follow existing code patterns in the repository
- Consult official Bluetooth SIG specs for all implementations
- Test thoroughly - no untested code
- Document your changes
- Keep PRs focused - one task per PR when possible

## Version Planning

**v0.4.0** (Next Release):
- Tasks 01-10 (Core improvements, async, docs)

**v1.0.0** (Major Release):
- Tasks 11-14 (Expansion, tooling, ecosystem)

**v2.0.0** (Future):
- Plugin ecosystem
- Language bindings
- Advanced features

---

Last Updated: 2025-01-11
Status: Ready for agent execution
Maintainer: @ronanb96
