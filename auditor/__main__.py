"""CLI entrypoint for Autonomous Repo Maintenance Agent."""

from .agent import MaintenanceRequest, RepoMaintenanceAgent


def main() -> None:
    agent = RepoMaintenanceAgent()
    request = MaintenanceRequest(
        title="Update outdated README setup instructions",
        description="Refresh onboarding steps and remove deprecated install commands.",
        constraints=["docs-only", "no runtime code changes"],
    )
    summary = agent.execute(".", request)
    print(summary.to_markdown())


if __name__ == "__main__":
    main()
