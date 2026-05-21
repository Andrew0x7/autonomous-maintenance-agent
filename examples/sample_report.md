# Example Maintenance Output

## Request

- Title: Update outdated README setup instructions
- Goal: Reduce confusion for first-time contributors
- Constraints: Edit documentation only, do not change runtime code

## Planned Files

- `README.md` — contains setup flow and onboarding details
- `docs/workflow.md` — documents maintenance execution steps
- `examples/sample_requests.md` — keeps example request wording aligned

## Applied Result

- standardized installation and maintenance wording
- removed noisy project framing
- aligned docs, examples, and prompts
- preserved narrow maintenance scope

## Validation

Current project run prints structured markdown summary through `python -m auditor`.

## Reviewer Summary

Task stayed inside low-risk documentation and packaging surface. Repository now shows clearer workflow, stronger project framing, and more inspectable artifacts for evaluator or maintainer.
