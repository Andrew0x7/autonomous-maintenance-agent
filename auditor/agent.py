"""
Main Orchestrator Agent.
Coordinates scanner, rule engine, LLM analyzer, and report generator.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import AuditConfig
from .scanner import ContractScanner
from .rules import RuleEngine, AuditResult
from .analyzer import LLMAnalyzer
from .report import ReportGenerator

logger = logging.getLogger(__name__)


class AuditAgent:
    """Orchestrator agent that coordinates the full audit pipeline."""

    def __init__(self, config: Optional[AuditConfig] = None):
        self.config = config or AuditConfig.from_env()
        self.rule_engine = RuleEngine()
        self.llm_analyzer = LLMAnalyzer(self.config.llm)
        self.report_gen = ReportGenerator(self.config.output_dir)

    def audit(
        self,
        address: str,
        chain: str = "ethereum",
        skip_llm: bool = False,
        output_format: str = "markdown",
    ) -> AuditResult:
        """Run full audit pipeline on a single contract."""
        chain_config = self.config.chains.get(chain)
        if not chain_config:
            raise ValueError(f"Unsupported chain: {chain}. Available: {list(self.config.chains.keys())}")

        # Step 1: Scan contract
        logger.info(f"[1/4] Scanning {address} on {chain}...")
        scanner = ContractScanner(chain_config)
        contract_data = scanner.scan(address)

        # Step 2: Run rule engine
        logger.info("[2/4] Running rule engine...")
        result = self.rule_engine.evaluate(contract_data)

        # Step 3: LLM enhancement (optional)
        if not skip_llm and contract_data.source_code:
            logger.info("[3/4] Running LLM analysis...")
            result = self.llm_analyzer.analyze(contract_data, result)
        else:
            logger.info("[3/4] Skipping LLM analysis")

        # Step 4: Generate report
        logger.info("[4/4] Generating report...")
        report_path = self.report_gen.generate(result, format=output_format)
        logger.info(f"Report saved: {report_path}")

        return result

    def batch_audit(
        self,
        addresses: list[tuple[str, str]],
        skip_llm: bool = False,
        output_format: str = "markdown",
    ) -> list[AuditResult]:
        """Run audit on multiple contracts."""
        results = []

        for address, chain in addresses:
            try:
                result = self.audit(address, chain, skip_llm, output_format)
                results.append(result)
                logger.info(
                    f"✓ {address[:10]}... — Score: {result.risk_score} ({result.risk_level})"
                )
            except Exception as e:
                logger.error(f"✗ {address[:10]}... — Error: {e}")

        # Generate batch summary
        if results:
            self.report_gen.generate_batch_summary(results)

        return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-Powered Smart Contract Auditor Agent"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Single scan
    scan_parser = subparsers.add_parser("scan", help="Scan a single contract")
    scan_parser.add_argument("address", help="Contract address")
    scan_parser.add_argument(
        "--chain", "-c", default="ethereum", help="Chain name (default: ethereum)"
    )
    scan_parser.add_argument(
        "--no-llm", action="store_true", help="Skip LLM analysis"
    )
    scan_parser.add_argument(
        "--format", "-f", choices=["markdown", "json"], default="markdown"
    )
    scan_parser.add_argument("--output", "-o", help="Output directory")

    # Batch scan
    batch_parser = subparsers.add_parser("batch", help="Batch scan from file")
    batch_parser.add_argument("file", help="File with addresses (one per line: address chain)")
    batch_parser.add_argument("--no-llm", action="store_true")
    batch_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    batch_parser.add_argument("--output", "-o", help="Output directory")

    # Report generation
    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_parser.add_argument("dir", help="Directory with audit JSON files")
    report_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # Load config
    env_path = str(Path(__file__).parent.parent / ".env")
    config = AuditConfig.from_env(env_path if Path(env_path).exists() else None)

    if hasattr(args, "output") and args.output:
        config.output_dir = args.output

    agent = AuditAgent(config)

    if args.command == "scan":
        result = agent.audit(args.address, args.chain, args.no_llm, args.format)
        print(f"\n{'='*60}")
        print(f"Risk Score: {result.risk_score}/100 ({result.risk_level})")
        print(f"Findings: {len(result.findings)}")
        print(f"{'='*60}")

    elif args.command == "batch":
        addresses = []
        with open(args.file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    addresses.append((parts[0], parts[1]))
                elif len(parts) == 1:
                    addresses.append((parts[0], "ethereum"))

        results = agent.batch_audit(addresses, args.no_llm, args.format)
        print(f"\nScanned {len(results)} contracts")
        for r in results:
            print(f"  {r.contract.address[:10]}... — Score: {r.risk_score} ({r.risk_level})")


if __name__ == "__main__":
    main()
