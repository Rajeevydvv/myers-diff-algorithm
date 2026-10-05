# Testing Guide — krkn-docs-bot-prototype

This document explains how to run, understand, and extend the test suite for the krkn Documentation Sync Bot.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Running the Tests](#running-the-tests)
5. [Test Modules](#test-modules)
   - [test_analyzer.py](#test_analyzerpy--15-tests)
   - [test_content_generator.py](#test_content_generatorpy--20-tests)
   - [test_hugo_writer.py](#test_hugo_writerpy--18-tests)
6. [Integration Testing with Real API](#integration-testing-with-real-api)
7. [Test Results Summary](#test-results-summary)
8. [Design Philosophy](#design-philosophy)
9. [Adding New Tests](#adding-new-tests)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The test suite contains **53 unit tests** across 3 modules. All tests are offline by default — they do not require a GitHub token or Anthropic API key. A separate integration path exists for testing against real APIs.

```
Total tests : 53
Passing     : 53
Failing     : 0
Runtime     : ~0.43 seconds
API calls   : 0 (unit tests use mocks and monkeypatching)
```

---

## Prerequisites

Install all dependencies before running tests:

```bash
pip install -r requirements.txt
```

Key testing dependencies from `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | 8.3.4 | Test runner |
| pytest-cov | 6.0.0 | Coverage reporting |
| PyGithub | 2.3.0 | GitHub API (used by analyzer) |
| anthropic | 0.40.0 | Claude API (used by content_generator) |

Python version required: **3.10 or higher** (tested on 3.13).

---

## Project Structure

```
krkn-docs-bot-prototype/
├── scripts/
│   └── doc_sync/
│       ├── analyzer.py            ← Semantic diff classifier
│       ├── content_generator.py   ← LLM documentation generator
│       └── hugo_writer.py         ← Hugo file writer and validator
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py           ← 15 tests
│   ├── test_content_generator.py  ← 20 tests
│   └── test_hugo_writer.py        ← 18 tests
├── demo.py                        ← Integration entry point
└── TESTING.md                     ← This file
```

---

## Running the Tests

### Run all tests

```bash
python -m pytest tests/
```

### Run with verbose output (see each test name)

```bash
python -m pytest tests/ -v
```

### Run a single test module

```bash
python -m pytest tests/test_analyzer.py -v
python -m pytest tests/test_content_generator.py -v
python -m pytest tests/test_hugo_writer.py -v
```

### Run a single specific test

```bash
python -m pytest tests/test_analyzer.py::test_detect_param_rename -v
```

### Run with coverage report

```bash
python -m pytest tests/ --cov=scripts/doc_sync --cov-report=term-missing
```

### Run and stop at first failure

```bash
python -m pytest tests/ -x
```

---

## Test Modules

---

### `test_analyzer.py` — 15 tests

Tests the semantic diff classifier in [scripts/doc_sync/analyzer.py](scripts/doc_sync/analyzer.py).

The analyzer is the entry point of the bot. It takes a list of changed files from a GitHub PR and classifies each one by its documentation impact — not just by raw line counts.

#### Functions tested

| Function | Description |
|----------|-------------|
| `classify_changes(files)` | Classifies each changed file by type and severity |
| `detect_param_rename(removed, added)` | Detects parameter renames using similarity matching |
| `is_doc_relevant(filename, patch)` | Pre-filter to skip non-documentation files |

#### Test list

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_classify_config_change` | A Python file with a new `int` field gets type `config_field_added` and severity `MEDIUM` |
| `test_detect_param_rename` | `kill_count` renamed to `disruption_count` is detected with confidence > 0.5 |
| `test_detect_param_rename_identical_lines_not_renamed` | Identical lines are not incorrectly flagged as renames |
| `test_is_doc_relevant_filters_test_files` | Files like `test_*.py` and `*_test.go` return `False` |
| `test_is_doc_relevant_filters_ci_configs` | `.github/workflows/*.yml`, `.travis.yml`, `.circleci/` return `False` |
| `test_is_doc_relevant_filters_go_sum` | `go.sum` changes return `False` |
| `test_is_doc_relevant_filters_package_lock` | `package-lock.json` changes return `False` |
| `test_is_doc_relevant_accepts_scenario_files` | Scenario Python files with new parameters return `True` |
| `test_is_doc_relevant_accepts_readme` | `README.md` always returns `True` |
| `test_is_doc_relevant_accepts_cli_file` | CLI command files (`cmd/root.go`) return `True` |
| `test_classify_new_scenario` | A newly added scenario class file gets type `new_scenario` and severity `HIGH` |
| `test_classify_cli_flag_change` | Changes in `cmd/*.go` files get type `cli_flag_change` and severity `MEDIUM` |
| `test_classify_readme_update` | `README.md` changes get type `readme_section_update` and severity `LOW` |
| `test_classify_no_doc_impact` | Vendor/dependency files get type `no_doc_impact` |
| `test_classify_mixed_batch` | A realistic PR with 3 files: 1 doc-relevant, 2 skipped — correctly split |

#### Example: running the rename detection test

```bash
python -m pytest tests/test_analyzer.py::test_detect_param_rename -v -s
```

Expected output:
```
PASSED  tests/test_analyzer.py::test_detect_param_rename
```

---

### `test_content_generator.py` — 20 tests

Tests the LLM documentation generator in [scripts/doc_sync/content_generator.py](scripts/doc_sync/content_generator.py).

These tests do **not** call the Claude API. They test prompt construction, response parsing, fallback behavior, and caching logic. The `ANTHROPIC_API_KEY` environment variable is explicitly deleted in relevant tests using `monkeypatch`.

#### Functions tested

| Function | Description |
|----------|-------------|
| `build_system_prompt(conventions)` | Builds the Claude system prompt from site conventions |
| `build_user_prompt(change, existing_content)` | Builds the per-request user prompt |
| `_parse_llm_response(text)` | Parses JSON from Claude's response text |
| `_fallback_response(change)` | Returns a template when the API is unavailable |
| `_cache_key(change, content)` | Generates a cache key for deduplication |
| `generate_doc_update(change, ...)` | Full generation pipeline (tested with no API key) |

#### Test list

**System prompt tests (5):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_prompt_includes_default_claude_md_conventions` | Prompt contains "front matter", `_tab-`, and "hugo" |
| `test_prompt_includes_custom_conventions` | Custom CLAUDE.md content overrides defaults |
| `test_prompt_specifies_no_front_matter_for_tabs` | Prompt explicitly prohibits `---` in tab files |
| `test_prompt_specifies_json_output` | Prompt instructs the model to return JSON |
| `test_prompt_specifies_all_three_tab_keys` | Prompt mentions `tab_krkn`, `tab_krkn_hub`, `tab_krknctl` |

**User prompt tests (4):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_user_prompt_includes_diff` | The raw git diff appears in the prompt |
| `test_user_prompt_includes_change_type_and_severity` | `param_rename` and `BREAKING` appear in the prompt |
| `test_user_prompt_includes_rename_notice` | Detected renames (`kill_count` → `disruption_count`) are highlighted |
| `test_user_prompt_includes_existing_content` | If existing doc content is provided, it appears under `EXISTING DOCUMENTATION` |

**Response parsing tests (4):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_parse_valid_json_response` | Clean JSON is parsed correctly |
| `test_parse_json_in_code_fence` | JSON wrapped in ` ```json ` fences is stripped and parsed |
| `test_parse_missing_keys_raises` | JSON missing required keys raises `ValueError` or `KeyError` |
| `test_parse_invalid_json_raises` | Plain text raises `ValueError` or `JSONDecodeError` |

**Fallback behavior tests (4):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_fallback_response_returns_all_three_tabs` | Fallback always returns `tab_krkn`, `tab_krkn_hub`, `tab_krknctl` |
| `test_fallback_includes_rename_notice` | Fallback for `param_rename` includes the old and new param names |
| `test_fallback_tab_krkn_has_no_front_matter` | Fallback content never starts with `---` |
| `test_fallback_confidence_is_zero` | Fallback sets `confidence = 0.0` to signal it is not LLM-generated |

**Integration tests (3, no API required):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_generate_returns_fallback_when_no_api_key` | Without `ANTHROPIC_API_KEY`, the function returns a fallback with `confidence = 0.0` |
| `test_generate_caches_identical_requests` | Two identical calls return the same object (cache hit) |

---

### `test_hugo_writer.py` — 18 tests

Tests the Hugo file writer in [scripts/doc_sync/hugo_writer.py](scripts/doc_sync/hugo_writer.py).

These tests use `tempfile.TemporaryDirectory()` so they write real files to a temporary location and clean up automatically. No changes are made to the actual repository.

#### Functions tested

| Function | Description |
|----------|-------------|
| `validate_tab_content(content, filename)` | Validates generated content before writing |
| `validate_front_matter(filepath, content)` | Checks front matter rules per file type |
| `get_target_files(change_type, repo, change, generated)` | Maps changes to target Hugo file paths |
| `write_tab_file(path, content, repo_path)` | Writes content to disk with safety checks |
| `create_scenario_directory(name, repo_path)` | Creates full scenario directory with all 4 files |

#### Test list

**Content validation tests (6):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_tab_file_has_no_front_matter` | Content starting with `---` is rejected for `_tab-*.md` files |
| `test_tab_file_valid_content` | Clean markdown content passes validation |
| `test_tab_file_rejects_hex_colors` | Hardcoded hex colors like `#EC1C24` are rejected |
| `test_tab_file_rejects_prism` | Prism.js stylesheet references are rejected |
| `test_tab_file_rejects_pre_tags` | `<pre>` HTML tags are rejected (use code fences instead) |
| `test_index_file_not_checked_for_front_matter` | `_index.md` is exempt from the no-front-matter rule |

**Front matter validation tests (5):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_validate_front_matter_tab_no_fm` | `_tab-krkn.md` without front matter passes |
| `test_validate_front_matter_tab_with_fm` | `_tab-krkn.md` with `---` front matter fails |
| `test_validate_front_matter_index_with_fm` | `_index.md` with `title:` in front matter passes |
| `test_validate_front_matter_index_missing_fm` | `_index.md` without any front matter fails |
| `test_validate_front_matter_index_missing_title` | `_index.md` with front matter but no `title:` field fails |

**File path mapping tests (3):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_correct_file_path_config_change` | `config_field_added` from `krkn-chaos/krkn` → `content/en/docs/scenarios/…/_tab-krkn.md` |
| `test_correct_file_path_cli_change` | `cli_flag_change` from `krkn-chaos/krknctl` → `content/en/docs/krknctl/…/_tab-krknctl.md` |
| `test_new_scenario_creates_all_tabs` | `new_scenario` change type returns all 4 files: `_tab-krkn.md`, `_tab-krkn-hub.md`, `_tab-krknctl.md`, `_index.md` |

**File write tests (2):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_write_tab_file_creates_file` | File is written at the correct path with correct content |
| `test_write_tab_file_rejects_front_matter` | `write_tab_file` returns `False` and writes nothing if content has front matter |

**Scenario directory creation tests (3):**

| Test Name | What It Verifies |
|-----------|-----------------|
| `test_create_scenario_directory_structure` | All 4 files are created and `written = True` for each |
| `test_create_scenario_directory_index_has_front_matter` | `_index.md` starts with `---` and contains `title:` |
| `test_create_scenario_directory_tabs_have_no_front_matter` | All three `_tab-*.md` files do not start with `---` |

---

## Integration Testing with Real API

The unit tests above use no external services. To test the full pipeline with a real GitHub PR and real Claude API:

### Step 1: Set up credentials

Create a `.env` file in the project root (never commit this file):

```bash
GITHUB_TOKEN=ghp_your_token_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

Or export them directly in your shell:

```bash
export GITHUB_TOKEN=ghp_your_token_here
export ANTHROPIC_API_KEY=sk-ant-your_key_here
```

### Step 2: Run the demo in dry-run mode

```bash
python demo.py --repo krkn-chaos/krkn --pr 939 --dry-run
```

This fetches the real PR from GitHub, calls Claude 4 times, generates documentation, validates it, and prints a preview. No PR is created on GitHub.

### Expected output (with API key)

```
Step 1  Fetching PR #939 from krkn-chaos/krkn...
        Found 6 changed files in: Post chaos virt checks

Step 2  Classifying changes semantically...
        4 doc-relevant change(s) found
        2 file(s) skipped (test files, CI configs, go.sum, etc.)

Step 3  Generating documentation...
        Processing: krkn/utils/VirtChecker.py (config_field_added)
        Calling Claude API...
        Confidence: 90%

Step 4  Validating generated content...
        Front matter validation passed

Step 5  Output...
        [Generated tab content preview]

Summary
        PR analyzed:        krkn-chaos/krkn#939
        Doc files targeted: 2
        Validation:         PASSED
```

### Run without API key (offline demo mode)

```bash
python demo.py --demo
```

Uses bundled mock data. No credentials needed. Good for CI pipelines and demonstrations.

---

## Test Results Summary

Results from the last full test run:

```
Platform : linux / Python 3.13.11
Runner   : pytest 8.3.4
Date     : 2026-05-17

tests/test_analyzer.py            15 passed
tests/test_content_generator.py   20 passed
tests/test_hugo_writer.py         18 passed
─────────────────────────────────────────────
TOTAL                             53 passed in 0.43s
```

All 53 tests pass with zero failures and zero warnings.

---

## Design Philosophy

### Why no API calls in unit tests?

Calling the Claude API or GitHub API in unit tests would:
- Make tests slow (1–5 seconds per call)
- Make tests flaky (network failures, rate limits)
- Cost money on every CI run

Instead, the tests verify the behavior of the functions themselves — prompt structure, response parsing, validation logic — by using `monkeypatch` to remove the `ANTHROPIC_API_KEY` and trigger the fallback path.

### Why use `tempfile.TemporaryDirectory()`?

`test_hugo_writer.py` tests actually write files to disk. Using `tempfile.TemporaryDirectory()` ensures:
- Tests do not pollute the repository
- Cleanup is automatic even if the test fails
- Tests can run in parallel safely

### Why test the pre-filter (`is_doc_relevant`) so thoroughly?

The `is_doc_relevant()` function is the cost control mechanism of the bot. If it lets through too many files, every CI run burns unnecessary Claude API credits. If it blocks too many files, real documentation changes get missed. It has 6 dedicated tests covering all the edge cases.

### Why test front matter so strictly?

A `_tab-*.md` file with front matter breaks the Hugo build silently — it may not show an error but the tab content disappears from the website. The validator catches this before any PR is created, ensuring zero broken PRs reach maintainers.

---

## Adding New Tests

### Adding a test for a new change type

Open [tests/test_analyzer.py](tests/test_analyzer.py) and follow this pattern:

```python
def test_classify_my_new_change():
    """Describe what scenario this tests."""
    files = [
        {
            "filename": "path/to/changed/file.py",
            "patch": "@@ -1,0 +1 @@\n+your diff content here",
            "additions": 1,
            "deletions": 0,
            "status": "modified",
        }
    ]
    results = classify_changes(files)
    assert results[0]["change_type"] == "expected_type"
    assert results[0]["severity"] == "MEDIUM"
```

### Adding a test for a new Hugo validation rule

Open [tests/test_hugo_writer.py](tests/test_hugo_writer.py) and follow this pattern:

```python
def test_tab_file_rejects_my_new_rule():
    """Describe what is being rejected and why."""
    bad_content = "## Content\n\nSome content with <forbidden-pattern> here\n"
    is_valid, error = validate_tab_content(bad_content, "_tab-krkn.md")
    assert not is_valid
    assert "keyword" in error.lower()
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'scripts'`

You are not running pytest from the project root. Run:

```bash
cd /path/to/krkn-docs-bot-prototype
python -m pytest tests/
```

### `ImportError: No module named 'github'`

Install dependencies:

```bash
pip install -r requirements.txt
```

### Tests pass locally but fail in CI

Check that the CI runner is using Python 3.10+:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
```

### `test_generate_returns_fallback_when_no_api_key` fails

This test uses `monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)` to remove the key. If your environment does not have the key set at all, `raising=False` prevents an error. The test should always pass regardless of whether the key is set.

If it fails, check that `generate_doc_update` in [scripts/doc_sync/content_generator.py](scripts/doc_sync/content_generator.py) reads `ANTHROPIC_API_KEY` from the environment at call time, not at import time.

---

*This testing guide covers the krkn-docs-bot-prototype as of 2026-05-17.*
*Reference issue: https://github.com/krkn-chaos/website/issues/320*