# Architecture

Autonomous Repo Maintenance Agent uses simple pipeline so reviewer can inspect logic fast.

## Components

### `auditor.agent.MaintenanceRequest`
Structured request object containing:
- title
- description
- constraints

### `auditor.agent.FileChange`
Represents target file and reason for inclusion.

### `auditor.agent.MaintenanceSummary`
Stores:
- planned files
- applied files
- validation result

Exposes `to_markdown()` so output can go directly into pull request notes or maintainer handoff.

### `auditor.agent.RepoMaintenanceAgent`
Implements end-to-end workflow:
1. inspect repository
2. plan candidate files
3. simulate scoped changes
4. emit validation note
5. return markdown summary

## Design choices

- plain dataclasses for inspectable state
- file tree matching for deterministic behavior
- markdown output for GitHub-native review flow
- small module size for easy extension

## Extension path

Future versions can add:
- repo policy adapters
- path allowlists and deny lists
- validation command runner
- diff summaries
- risk scoring per task
