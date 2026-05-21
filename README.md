# Autonomous Maintenance Agent

Autonomous Maintenance Agent helps small teams turn repetitive repository upkeep into a structured, file-aware workflow.

It focuses on practical maintenance work: reading a maintenance request, scanning repository files, identifying likely targets, preparing scoped changes, and returning a clear markdown summary for handoff.

```text
┌─────────────────────┐
│ Maintenance Request │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Repository Scan     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Keyword + Path Plan │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Scoped File Changes │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Validation Summary  │
└─────────────────────┘
```

## ✨ Features

- 🔎 Repository scan before planning changes
- 🧭 Keyword-based file targeting for narrow maintenance tasks
- 📝 Markdown summary for planned files, applied files, and validation status
- 🧱 Minimal Python package structure with CLI entrypoint
- 📚 Included docs, prompts, and example artifacts for extension
- 🔁 Repeatable workflow for documentation upkeep, config refreshes, and low-risk maintenance tasks

## 🚀 Why it exists

Small teams often lose time on maintenance work that is not hard, but repeats constantly:

- outdated setup instructions
- stale configuration examples
- small cleanup requests with vague scope
- repetitive repository hygiene tasks
- weak handoff notes after narrow edits

This project exists to keep that work structured, traceable, and easier to continue over time.

## 📦 Installation

### Requirements

- Python 3.11+
- Git

### Clone repository

```bash
git clone https://github.com/Andrew0x7/autonomous-maintenance-agent.git
cd autonomous-maintenance-agent
```

### Install from source

```bash
pip install -e .
```

### Alternative install with requirements file

```bash
pip install -r requirements.txt
```

### Verify package entrypoint

```bash
python -m auditor
```

Or use script entrypoint defined in `pyproject.toml`:

```bash
repo-maintainer
```

## ⚙️ What happens when it runs

Current CLI entrypoint creates a sample maintenance request and executes the full workflow against the current repository.

Default request:

```text
Title: Update outdated README setup instructions
Description: Refresh onboarding steps and remove deprecated install commands.
Constraints: docs-only, no runtime code changes.
```

Execution flow:

1. inspect repository files
2. extract keywords from title and description
3. match likely target files
4. build scoped maintenance plan
5. generate applied-file summary
6. return markdown output

## 🧪 Quick Start

### 1) Clone project

```bash
git clone https://github.com/Andrew0x7/autonomous-maintenance-agent.git
cd autonomous-maintenance-agent
```

### 2) Install package

```bash
pip install -e .
```

### 3) Run agent

```bash
python -m auditor
```

### 4) Expected output shape

```text
# Maintenance Summary: Update outdated README setup instructions

## Planned Files
- `README.md` — Matched request keywords

## Applied Files
- `README.md` — Updated for maintenance task: Matched request keywords

## Validation
Validation placeholder: run repo-specific tests or lint commands here.
```

## 🛠️ Usage

### Run with module entrypoint

```bash
python -m auditor
```

### Run with installed console script

```bash
repo-maintainer
```

### Run inside a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m auditor
```

### Build distribution artifacts

```bash
python -m build
```

### Inspect package metadata

```bash
python - <<'PY'
from importlib.metadata import metadata
m = metadata('autonomous-maintenance-agent')
print(m['Name'])
print(m['Version'])
print(m['Summary'])
PY
```

## 📋 Example Request

Current code uses a built-in request object in `auditor/__main__.py`:

```python
request = MaintenanceRequest(
    title="Update outdated README setup instructions",
    description="Refresh onboarding steps and remove deprecated install commands.",
    constraints=["docs-only", "no runtime code changes"],
)
```

You can modify that request and run again:

```bash
python -m auditor
```

Example request ideas:

```text
Title: Refresh stale configuration examples
Description: Update config docs to match current environment variable names.
Constraints: docs-only, config-only
```

```text
Title: Clean up onboarding guide
Description: Remove deprecated setup steps and align quick start commands.
Constraints: markdown-only
```

```text
Title: Review helper module references
Description: Identify likely files affected by a narrow helper rename.
Constraints: no runtime edits
```

## 📤 Example Output

The agent returns a markdown summary with:

- request title
- planned files
- applied files
- validation note

Sample output:

```markdown
# Maintenance Summary: Update outdated README setup instructions

## Planned Files
- `README.md` — Matched request keywords
- `docs/workflow.md` — Matched request keywords

## Applied Files
- `README.md` — Updated for maintenance task: Matched request keywords
- `docs/workflow.md` — Updated for maintenance task: Matched request keywords

## Validation
Validation placeholder: run repo-specific tests or lint commands here.
```

## 🧠 How file selection works

Keyword extraction happens from request title and description.

High-level behavior in `auditor/agent.py`:

- lowercase request text
- remove short and noisy tokens
- scan repository files recursively
- skip noisy paths like `.git/`, `__pycache__/`, `.pytest_cache/`
- match file paths against normalized keywords
- fall back to high-signal files if nothing matches

Current fallback files:

```text
README.md
docs/overview.md
src/main.py
```

Candidate list is limited to first 8 matches.

## 🗂️ Project Structure

```text
auditor/
  __init__.py
  __main__.py
  agent.py
examples/
  sample_report.md
  sample_requests.md
docs/
  architecture.md
  evaluation.md
  workflow.md
prompts/
  repo_request.md
  system_prompt.md
CHANGELOG.md
CONTRIBUTING.md
CONTRIBUTORS.md
LICENSE
MANIFEST.in
pyproject.toml
README.md
requirements.txt
```

## 🔧 Development

### Run module directly during development

```bash
python -m auditor
```

### Read CLI entrypoint

```bash
python - <<'PY'
from pathlib import Path
print(Path('auditor/__main__.py').read_text())
PY
```

### Read core workflow

```bash
python - <<'PY'
from pathlib import Path
print(Path('auditor/agent.py').read_text())
PY
```

### Check git status after changes

```bash
git status --short
```

### Create a release tag

```bash
git tag v0.1.0
git push origin v0.1.0
```

## 📚 Included Documentation

- `docs/architecture.md` — architecture overview
- `docs/workflow.md` — workflow and summary format
- `docs/evaluation.md` — evaluation notes and scope
- `prompts/system_prompt.md` — base system behavior
- `prompts/repo_request.md` — request template
- `examples/sample_requests.md` — example inputs
- `examples/sample_report.md` — example output artifact

## 🎯 Good fit for this project

Use this project when you want to explore or extend workflows like:

- repository maintenance assistants
- scoped documentation refresh tools
- config upkeep helpers
- human-in-the-loop maintenance automation
- file-aware planning before edits

## ⚠️ Current limits

- current CLI uses a built-in sample request
- validation step is placeholder text
- no live file patching yet
- no external model call in runtime path yet
- best suited for narrow maintenance scenarios, not broad codebase rewrites

## 🤖 Anthropic Claude Opus role

Current version was developed with Anthropic Claude Opus as reasoning model for:

- request interpretation
- scope planning
- file selection logic
- summary generation style
- maintenance workflow design

Model use is visible in prompts, docs, examples, and contributor attribution.

## 🗺️ Next extensions

```text
- connect repo-specific validation commands
- add policy rules for protected paths
- support ignore lists per project
- score maintenance plans by risk level
- export JSON summary for CI pipelines
```

## 📄 License

MIT License. See `LICENSE`.
