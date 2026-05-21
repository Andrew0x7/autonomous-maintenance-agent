# Workflow

## Request intake

Agent accepts plain-English maintenance request plus optional constraints.

## Repository inspection

Agent walks repository path recursively and collects file list.

## Candidate planning

Agent extracts request keywords, normalizes them, skips noisy folders, and selects matching files.

## Change application

Current version simulates targeted maintenance updates by mapping planned files to applied files with explicit reason strings.

## Validation

Current validation step returns placeholder message so each integrating repository can inject own test, lint, or docs build command.

## Summary output

Agent returns markdown summary with:
- request title
- planned files
- applied files
- validation section

This output is optimized for maintainer handoff and issue tracking.
