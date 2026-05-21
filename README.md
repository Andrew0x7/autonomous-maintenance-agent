# Autonomous Maintenance Agent

Autonomous Maintenance Agent helps small teams handle repetitive repository upkeep without turning every maintenance task into manual overhead.

It was built around practical maintainer work: triaging narrow requests, finding the right files, preparing scoped changes, validating those changes, and leaving a clear handoff for the next person who touches the repository.

Instead of treating maintenance as loose chat output, this project turns it into a structured, file-aware workflow.

## Why it exists

Repository maintenance is rarely difficult in isolation, but it becomes expensive when repeated every week.

Common friction points:

- small maintenance requests arrive with vague scope
- teams touch the wrong files or miss related docs
- routine cleanup steals time from feature work
- handoff notes are inconsistent or incomplete
- repeated upkeep slowly creates drift across repository files

Autonomous Maintenance Agent exists to make that work more predictable, more traceable, and easier to continue over time.

## What it helps with

- issue triage for narrow maintenance tasks
- repository inspection before edits
- file-aware planning for low-risk updates
- documentation and configuration upkeep
- structured change summaries for human handoff
- repeatable maintenance flow for small teams

## How it works

```text
Maintenance request
    ↓
Repository scan
    ↓
Keyword + path matching
    ↓
Scoped file plan
    ↓
Targeted edits
    ↓
Validation step
    ↓
Maintenance summary
```

The goal is not to replace maintainers. The goal is to reduce repetitive repository work while keeping decisions grounded in project context.

## Core workflow

1. Accept a maintenance request in plain English.
2. Scan repository structure for likely target files.
3. Ignore noisy paths like `.git/` and `__pycache__/`.
4. Build a constrained file-level plan from request keywords.
5. Apply scoped updates only to matched files.
6. Run validation or repo-specific follow-up checks.
7. Produce a clear maintenance summary for handoff.

## Design goals

- keep maintenance tasks narrow and explainable
- reduce wasted time on repetitive repo chores
- keep file selection grounded in repository structure
- support human-in-the-loop decisions where needed
- make maintenance output easy to reuse in future tasks

## Example use cases

- refresh outdated onboarding docs
- update stale configuration examples
- isolate low-risk helper refactors
- convert rough maintenance note into file plan
- generate structured follow-up summary after edits
- support maintainers working across many small repositories

## Inputs

- local repository path
- maintenance request title
- maintenance request description
- optional constraints
- optional validation command

## Outputs

- planned file list
- applied file list
- validation status
- markdown maintenance summary
- reusable prompts and examples for future tasks

## Repository layout

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
  workflow.md
  evaluation.md
prompts/
  system_prompt.md
  repo_request.md
CHANGELOG.md
CONTRIBUTING.md
CONTRIBUTORS.md
MANIFEST.in
pyproject.toml
README.md
requirements.txt
```

## Example workflow

Request:

```text
Title: Update outdated README setup instructions
Description: Refresh onboarding steps and remove deprecated install commands.
Constraints: docs-only, no runtime code changes.
```

Result:

- agent scans repo tree
- `README.md` and related docs match request keywords
- agent plans docs-only changes
- validation returns repo-specific next step
- summary explains what changed and why

## Quick start

```bash
python -m auditor
```

Expected output: markdown maintenance summary for sample request.

## Architecture notes

The repository is intentionally small and direct.

- prompts define request interpretation behavior
- docs explain workflow and evaluation flow
- examples show expected inputs and outputs
- package metadata keeps installation and entrypoints explicit
- release history tracks public project milestones

This keeps the project practical for development, experimentation, and gradual extension.

## Anthropic Claude Opus role

Current version was developed with Anthropic Claude Opus as reasoning model for:

- request interpretation
- scope planning
- file selection logic
- summary generation style
- maintenance workflow design

Model use is visible in prompts, docs, examples, and contributor attribution.

## Next extensions

- connect repo-specific validation commands
- add policy rules for protected paths
- support ignore lists per project
- score maintenance plans by risk level
- export JSON summary for CI pipelines
