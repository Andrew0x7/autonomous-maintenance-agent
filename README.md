# Maintainer Flow

Maintainer Flow turns repetitive repository upkeep into structured, file-aware workflow.

Instead of asking maintainer to inspect repo, guess scope, edit files manually, then write reviewer notes, agent handles full maintenance loop:

- read maintenance request
- inspect repository structure
- identify likely target files
- plan constrained edits
- apply scoped changes
- run validation hooks
- produce reviewer-ready summary

Project built around practical developer pain: small teams lose hours on doc drift, stale config, narrow refactors, repetitive hygiene tasks, and weak merge handoff. This agent standardizes those tasks into predictable pipeline with visible artifacts.

## Why this matters

Repository maintenance usually fails for boring reasons:

- issue scope too broad
- maintainer touches wrong files
- docs and code drift apart
- reviewers receive vague summaries
- repetitive tasks steal focus from product work

This project reduces maintenance overhead by converting plain-English request into narrow, auditable execution path.

## Core workflow

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
Review-ready markdown summary
```

## What agent does

1. Accepts task request in plain English.
2. Scans repository tree for candidate files.
3. Filters noisy directories like `.git/` and `__pycache__/`.
4. Builds file-level plan from request keywords.
5. Applies scoped updates only to matched files.
6. Preserves traceable before/after reasoning.
7. Emits markdown summary for reviewer or maintainer.

## Why this is not generic AI wrapper

Many coding demos stop at freeform text output. This project focuses on operational repo work:

- repository inspection, not chat-only generation
- file-level planning, not broad rewrite guessing
- constrained maintenance scope, not vague assistance
- markdown artifacts reviewer can inspect directly
- repeatable workflow maintainers can adapt per repo

## Primary use cases

- refresh outdated onboarding docs
- update stale configuration examples
- isolate low-risk helper refactors
- convert rough maintenance note into file plan
- generate structured reviewer summary after edits
- reduce reviewer effort on small but frequent repo chores

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

## Why this repo is easy to review

This repo is small, concrete, and easy to inspect. A reviewer can open it and immediately see workflow, prompts, package metadata, release notes, example inputs, and output artifact. It shows agentic file reasoning inside real repository work instead of generic chatbot behavior.

## Anthropic Claude Opus role

Current version was developed with Anthropic Claude Opus as reasoning model for:

- request interpretation
- scope planning
- file selection logic
- summary generation style
- maintenance workflow design

Model use is visible in prompts, docs, examples, and contributor attribution.

## Quick start

```bash
python -m auditor
```

Expected output: markdown maintenance summary for sample request.

## Next extensions

- connect repo-specific validation commands
- add policy rules for protected paths
- support ignore lists per project
- score maintenance plans by risk level
- export JSON summary for CI pipelines
