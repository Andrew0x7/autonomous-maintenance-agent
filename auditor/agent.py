"""Core workflow for Autonomous Repo Maintenance Agent."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import re


@dataclass
class MaintenanceRequest:
    title: str
    description: str
    constraints: list[str]


@dataclass
class FileChange:
    path: str
    reason: str


@dataclass
class MaintenanceSummary:
    request_title: str
    planned_files: list[FileChange]
    applied_files: list[FileChange]
    validation: str

    def to_markdown(self) -> str:
        lines = [
            f"# Maintenance Summary: {self.request_title}",
            "",
            "## Planned Files",
        ]
        for item in self.planned_files:
            lines.append(f"- `{item.path}` — {item.reason}")

        lines.extend(["", "## Applied Files"])
        for item in self.applied_files:
            lines.append(f"- `{item.path}` — {item.reason}")

        lines.extend(["", "## Validation", self.validation])
        return "\n".join(lines)


class RepoMaintenanceAgent:
    """Minimal autonomous maintenance workflow for repository tasks."""

    def inspect_repository(self, repo_path: str) -> list[str]:
        root = Path(repo_path)
        return sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())

    def plan_changes(self, request: MaintenanceRequest, repo_files: Iterable[str]) -> list[FileChange]:
        files = list(repo_files)
        candidates: list[FileChange] = []
        raw_keywords = set(request.title.lower().split()) | set(request.description.lower().split())
        keywords = {
            re.sub(r"[^a-z0-9_.-]", "", word)
            for word in raw_keywords
            if len(re.sub(r"[^a-z0-9_.-]", "", word)) >= 4
        }
        ignored_prefixes = (".git/", "__pycache__/", ".pytest_cache/")

        for file_path in files:
            if file_path.startswith(ignored_prefixes):
                continue
            lowered = file_path.lower()
            if any(word in lowered for word in keywords):
                candidates.append(FileChange(path=file_path, reason="Matched request keywords"))

        if not candidates:
            for default_file in ["README.md", "docs/overview.md", "src/main.py"]:
                if default_file in files:
                    candidates.append(FileChange(path=default_file, reason="Fallback high-signal file"))

        return candidates[:8]

    def apply_changes(self, plan: list[FileChange]) -> list[FileChange]:
        return [
            FileChange(path=item.path, reason=f"Updated for maintenance task: {item.reason}")
            for item in plan
        ]

    def validate(self) -> str:
        return "Validation placeholder: run repo-specific tests or lint commands here."

    def execute(self, repo_path: str, request: MaintenanceRequest) -> MaintenanceSummary:
        repo_files = self.inspect_repository(repo_path)
        planned = self.plan_changes(request, repo_files)
        applied = self.apply_changes(planned)
        validation = self.validate()
        return MaintenanceSummary(
            request_title=request.title,
            planned_files=planned,
            applied_files=applied,
            validation=validation,
        )
