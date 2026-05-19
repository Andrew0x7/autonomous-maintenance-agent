"""
Detection rule engine for smart contract vulnerabilities.
Pattern-based + bytecode analysis without requiring source code.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .scanner import ContractData


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """Single audit finding."""
    rule_id: str
    title: str
    description: str
    risk: RiskLevel
    confidence: float  # 0.0 - 1.0
    location: Optional[str] = None
    recommendation: str = ""
    evidence: str = ""


@dataclass
class AuditResult:
    """Complete audit result for a contract."""
    contract: ContractData
    findings: list[Finding] = field(default_factory=list)
    risk_score: int = 0  # 0-100, higher = more dangerous
    summary: str = ""

    def add_finding(self, finding: Finding):
        self.findings.append(finding)

    @property
    def risk_level(self) -> str:
        if self.risk_score >= 90:
            return "CRITICAL"
        elif self.risk_score >= 70:
            return "HIGH"
        elif self.risk_score >= 40:
            return "MEDIUM"
        return "LOW"


class RuleEngine:
    """Pattern-based vulnerability detection rules."""

    def __init__(self):
        self.rules = [
            self._check_hidden_mint,
            self._check_honeypot_sell,
            self._check_blacklist,
            self._check_proxy_no_timelock,
            self._check_excessive_owner,
            self._check_selfdestruct,
            self._check_fee_manipulation,
            self._check_unchecked_external,
            self._check_tx_origin,
            self._check_assembly_risk,
        ]

    def evaluate(self, data: ContractData) -> AuditResult:
        """Run all rules against contract data."""
        result = AuditResult(contract=data)

        for rule_func in self.rules:
            findings = rule_func(data)
            for f in findings:
                result.add_finding(f)

        # Calculate composite risk score
        result.risk_score = self._calculate_score(result)
        result.summary = self._generate_summary(result)

        return result

    def _check_hidden_mint(self, data: ContractData) -> list[Finding]:
        """Detect privileged mint functions."""
        findings = []
        mint_patterns = [
            r"function\s+mint\s*\(",
            r"function\s+_mint\s*\(",
            r"function\s+emergencyMint\s*\(",
            r"function\s+batchMint\s*\(",
        ]

        for pattern in mint_patterns:
            matches = re.findall(pattern, data.source_code, re.IGNORECASE)
            if matches:
                # Check if it has access control
                has_only_owner = bool(
                    re.search(
                        r"onlyOwner|onlyAdmin|onlyMinter|require\s*\(\s*msg\.sender",
                        data.source_code,
                    )
                )
                if not has_only_owner:
                    findings.append(
                        Finding(
                            rule_id="HIDDEN-MINT-001",
                            title="Unrestricted Mint Function",
                            description=(
                                "Contract contains mint function without access control. "
                                "Anyone can mint unlimited tokens."
                            ),
                            risk=RiskLevel.CRITICAL,
                            confidence=0.9,
                            recommendation="Add onlyOwner or role-based access control to mint functions.",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            rule_id="HIDDEN-MINT-002",
                            title="Owner-Only Mint Function",
                            description=(
                                "Contract has owner-restricted mint function. "
                                "Owner can mint unlimited tokens at any time."
                            ),
                            risk=RiskLevel.HIGH,
                            confidence=0.85,
                            recommendation=(
                                "Consider adding supply cap, timelock, or multi-sig requirement."
                            ),
                        )
                    )
        return findings

    def _check_honeypot_sell(self, data: ContractData) -> list[Finding]:
        """Detect honeypot patterns — buy allowed, sell restricted."""
        findings = []
        source = data.source_code.lower()

        # Patterns that restrict selling
        sell_restrictors = [
            (r"require\s*\(\s*.*block\.number.*\)", "Block number restriction on sell"),
            (r"mapping.*=>.*bool.*blacklist", "Blacklist mapping found"),
            (r"onlywhitelist|onlywhitelisted", "Whitelist-only transfer"),
            (r"trading\s*=\s*false", "Trading disabled by default"),
            (r"maxtxamount\s*=\s*0", "Max transaction amount set to zero"),
        ]

        for pattern, desc in sell_restrictors:
            if re.search(pattern, source):
                findings.append(
                    Finding(
                        rule_id="HONEYPOT-001",
                        title="Potential Honeypot Pattern",
                        description=f"Sell restriction detected: {desc}",
                        risk=RiskLevel.CRITICAL,
                        confidence=0.8,
                        recommendation="Verify transfer functions allow free selling. High rug risk.",
                    )
                )
        return findings

    def _check_blacklist(self, data: ContractData) -> list[Finding]:
        """Detect blacklist/greylist mechanisms."""
        findings = []
        if re.search(r"mapping\s*\(.*address.*=>.*bool.*\)\s*(public\s+)?is[Bb]lack", data.source_code):
            findings.append(
                Finding(
                    rule_id="BLACKLIST-001",
                    title="Address Blacklist Mechanism",
                    description="Contract implements address blacklist. Owner can block any address from transferring.",
                    risk=RiskLevel.MEDIUM,
                    confidence=0.9,
                    recommendation="Verify blacklist cannot be abused to freeze user funds indefinitely.",
                )
            )
        return findings

    def _check_proxy_no_timelock(self, data: ContractData) -> list[Finding]:
        """Detect upgradeable proxies without timelock."""
        findings = []
        if data.is_proxy:
            has_timelock = bool(
                re.search(r"timelock|timelockcontroller|delay", data.source_code, re.IGNORECASE)
            )
            if not has_timelock:
                findings.append(
                    Finding(
                        rule_id="PROXY-001",
                        title="Upgradeable Proxy Without Timelock",
                        description=(
                            f"Proxy contract detected (impl: {data.implementation_address}). "
                            "No timelock found — admin can upgrade instantly without delay."
                        ),
                        risk=RiskLevel.HIGH,
                        confidence=0.95,
                        recommendation="Add TimelockController or minimum 48h delay for upgrades.",
                    )
                )
        return findings

    def _check_excessive_owner(self, data: ContractData) -> list[Finding]:
        """Detect excessive owner privileges."""
        findings = []
        owner_functions = re.findall(
            r"function\s+(\w+).*onlyOwner", data.source_code, re.IGNORECASE
        )
        if len(owner_functions) > 10:
            findings.append(
                Finding(
                    rule_id="OWNER-001",
                    title="Excessive Owner Privileges",
                    description=f"Owner has access to {len(owner_functions)} privileged functions: {', '.join(owner_functions[:5])}...",
                    risk=RiskLevel.MEDIUM,
                    confidence=0.7,
                    recommendation="Reduce owner privileges. Use role-based access control (AccessControl).",
                )
            )
        return findings

    def _check_selfdestruct(self, data: ContractData) -> list[Finding]:
        """Detect selfdestruct usage."""
        findings = []
        if re.search(r"selfdestruct|suicide", data.source_code, re.IGNORECASE):
            findings.append(
                Finding(
                    rule_id="DESTRUCT-001",
                    title="Self-Destruct Function",
                    description="Contract contains selfdestruct — can be permanently destroyed, sending all ETH to arbitrary address.",
                    risk=RiskLevel.HIGH,
                    confidence=0.95,
                    recommendation="Remove selfdestruct. Use pause pattern instead if needed.",
                )
            )
        return findings

    def _check_fee_manipulation(self, data: ContractData) -> list[Finding]:
        """Detect dynamic fee structures that can be manipulated."""
        findings = []
        if re.search(r"fee\s*=.*\d+.*fee\s*=", data.source_code, re.IGNORECASE):
            if re.search(r"onlyOwner.*fee|fee.*onlyOwner", data.source_code, re.IGNORECASE):
                findings.append(
                    Finding(
                        rule_id="FEE-001",
                        title="Owner-Manipulable Fee Structure",
                        description="Fee percentage can be changed by owner without restriction.",
                        risk=RiskLevel.MEDIUM,
                        confidence=0.75,
                        recommendation="Add maximum fee cap (e.g., max 10%) enforced in code.",
                    )
                )
        return findings

    def _check_unchecked_external(self, data: ContractData) -> list[Finding]:
        """Detect unchecked return values from external calls."""
        findings = []
        # Look for .call{value: without checking return
        if re.search(r"\.call\{.*\}\s*\(\s*\)", data.source_code):
            findings.append(
                Finding(
                    rule_id="EXTCALL-001",
                    title="Unchecked External Call Return Value",
                    description="External call return value not checked — silent failure possible.",
                    risk=RiskLevel.MEDIUM,
                    confidence=0.7,
                    recommendation="Always check return value: (bool success, ) = addr.call{value: x}(\"\"); require(success);",
                )
            )
        return findings

    def _check_tx_origin(self, data: ContractData) -> list[Finding]:
        """Detect tx.origin for authentication."""
        findings = []
        if re.search(r"require\s*\(.*tx\.origin", data.source_code):
            findings.append(
                Finding(
                    rule_id="TXORIGIN-001",
                    title="tx.origin Used for Authentication",
                    description="tx.origin used in require — vulnerable to phishing attacks via intermediary contract.",
                    risk=RiskLevel.HIGH,
                    confidence=0.9,
                    recommendation="Use msg.sender instead of tx.origin for authentication.",
                )
            )
        return findings

    def _check_assembly_risk(self, data: ContractData) -> list[Finding]:
        """Detect inline assembly usage."""
        findings = []
        assembly_blocks = re.findall(r"assembly\s*\{", data.source_code)
        if len(assembly_blocks) > 3:
            findings.append(
                Finding(
                    rule_id="ASSEMBLY-001",
                    title="Excessive Inline Assembly",
                    description=f"Contract contains {len(assembly_blocks)} assembly blocks — bypasses Solidity safety checks.",
                    risk=RiskLevel.MEDIUM,
                    confidence=0.6,
                    recommendation="Review assembly blocks carefully. Consider using Solidity native functions.",
                )
            )
        return findings

    def _calculate_score(self, result: AuditResult) -> int:
        """Calculate composite risk score from findings."""
        if not result.findings:
            return 0

        weights = {
            RiskLevel.CRITICAL: 40,
            RiskLevel.HIGH: 25,
            RiskLevel.MEDIUM: 10,
            RiskLevel.LOW: 3,
            RiskLevel.INFO: 0,
        }

        score = sum(
            weights.get(f.risk, 0) * f.confidence for f in result.findings
        )
        return min(100, int(score))

    def _generate_summary(self, result: AuditResult) -> str:
        """Generate human-readable summary."""
        counts = {}
        for f in result.findings:
            counts[f.risk.value] = counts.get(f.risk.value, 0) + 1

        parts = [f"{count} {level.upper()}" for level, count in counts.items() if count > 0]
        return f"Risk Score: {result.risk_score}/100 ({result.risk_level}) — Findings: {', '.join(parts) if parts else 'None'}"
