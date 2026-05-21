# Evaluation

## What maintainers can verify quickly

- README explains problem and workflow
- package metadata exists in `pyproject.toml`
- release notes exist in `CHANGELOG.md`
- contributor attribution exists in `CONTRIBUTORS.md`
- prompts show model-oriented repo maintenance framing
- examples show request and report artifact
- running `python -m auditor` prints structured markdown output

## Strengths

- concrete niche: repository maintenance
- visible file reasoning
- clear artifact output
- small codebase, low maintenance overhead

## Limits

- current version does not modify real files automatically
- validation hook is placeholder until connected to repo-specific commands
- planning heuristic is keyword-based, not semantic retrieval

## Why this still works

Project is easy to inspect, easy to run, and easy to understand. Maintainers can map request to output without reading a large codebase.
