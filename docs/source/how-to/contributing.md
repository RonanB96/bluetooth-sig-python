# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/ronanb96/bluetooth-sig-python/issues>.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

Bluetooth SIG Python could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at <https://github.com/ronanb96/bluetooth-sig-python/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started

Ready to contribute? Here's how to set up `bluetooth_sig_python` for local development.

1. Fork the `bluetooth_sig_python` repo on GitHub.

1. Clone your fork locally:

   ```sh
   git clone git@github.com:your_name_here/bluetooth-sig-python.git
   ```

1. Install your local copy into a virtualenv:

   ```sh
   cd bluetooth-sig-python/
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

1. Create a branch for local development:

   ```sh
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

1. When you're done making changes, check that your changes pass the quality checks and tests:

   ```sh
   ./scripts/format.sh --fix    # Fix formatting
   ./scripts/lint.sh --all      # Run all linting
   python -m pytest tests/     # Run tests
   ```

1. Commit your changes and push your branch to GitHub:

   ```sh
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

1. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
1. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
1. The pull request should work for Python 3.10+. Tests run in GitHub Actions on every pull request to the main branch, make sure that the tests pass for all supported Python versions.

## Maintainer Workflow: SIG Spec Validation

These steps are for **maintainers** validating that Python service implementations match Bluetooth SIG specification tables. They are **not** CI gates—SIG HTML fetch requires manual steps and local spec extracts.

### Prerequisites

- Development environment installed (`pip install -e ".[dev]"`)
- Familiarity with [Fetching SIG Specs](https://github.com/RonanB96/bluetooth-sig-python/blob/main/.github/copilot-instructions.md#fetching-sig-specs) in `.github/copilot-instructions.md`

### 1. Extract spec text into `.tmp/`

1. Find the service spec slug on [Bluetooth SIG Specifications](https://www.bluetooth.com/specifications/specs/).
2. Follow the copilot instructions to resolve the public HTML URL (one spec at a time; do not guess URL patterns).
3. Save plain-text extracts of the characteristics table section as `.tmp/{service-name}_spec.txt` (filename must end with `_spec.txt`).

The `.tmp/` directory is gitignored—spec extracts stay local.

### 2. Run the validation script

```bash
python scripts/validate_service_characteristics_from_specs.py
python scripts/validate_service_characteristics_from_specs.py --verbose
python scripts/validate_service_characteristics_from_specs.py --spec-dir .tmp --pattern '*_spec.txt'
```

The script compares parsed spec tables to `src/bluetooth_sig/gatt/services/` implementations. Exit code **0** means all matched services align; **1** means mismatches or unmatched spec files.

Interpret the summary:

- **Service mismatches** — mandatory characteristics missing from Python, extra characteristics, or requirement-flag differences
- **Unmatched specs** — spec file could not be mapped to a service class (often naming or out-of-scope domains)
- **Parse skips** — file had no parseable characteristics table

### 3. Run the coverage companion

```bash
python scripts/gatt_coverage_report.py
python scripts/gatt_coverage_report.py --verbose
```

This reports YAML → Python gaps for characteristics, services, and descriptors. Use it to prioritize implementation backlog.

### 4. When to file issues vs mark out-of-scope

File implementation issues when a **BLE GATT** service or characteristic is in scope but missing or wrong. Mark out-of-scope (do not block on validation) for:

- **Mesh networking** — different protocol stack ([registry coverage](../reference/registry-coverage.md))
- **Classic Bluetooth / SDP** — `service_discovery/` registries
- **LE Audio / profile-triggered registries** — loaded as corresponding GATT services are implemented

Run ``python scripts/gatt_coverage_report.py --verbose`` for the current characteristic/service backlog.

See [Registry Coverage](../reference/registry-coverage.md) for the full out-of-scope list and priority roadmap.

### Downstream custom parsers

Integrators can register vendor-specific parsers outside this repo; see [Adding Characteristics — companion packages](adding-characteristics.md) (extension model).

## Tips

To run a subset of tests:

```sh
python -m pytest tests/test_specific_module.py
```

## Deploying

A reminder for the maintainers on how to deploy. Make sure all your changes are committed (including an entry in HISTORY.md). Then run:

```sh
bump2version patch # possible: major / minor / patch
git push
git push --tags
```

You can set up a [GitHub Actions workflow](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python#publishing-to-pypi) to automatically deploy your package to PyPI when you push a new tag.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](../community/code-of-conduct.md). By participating in this project you agree to abide by its terms.
