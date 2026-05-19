"""
LLM-powered smart contract analysis.
Uses Claude / MiMo / DeepSeek for intelligent pattern recognition
beyond static rules.
"""

import json
import logging
from typing import Optional

import requests

from .config import LLMConfig
from .scanner import ContractData
from .rules import AuditResult, Finding, RiskLevel

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """You are a senior smart contract security auditor. Analyze the following contract data and identify security vulnerabilities.

Contract Address: {address}
Chain: {chain}
Compiler: {compiler}
Is Proxy: {is_proxy}
Implementation: {implementation}

Functions found:
{functions}

Source code (first 8000 chars):
```solidity
{source}
```

Provide your analysis in this exact JSON format:
{{
  "findings": [
    {{
      "rule_id": "LLM-XXX",
      "title": "Short title",
      "description": "Detailed explanation of the vulnerability",
      "risk": "critical|high|medium|low",
      "confidence": 0.0-1.0,
      "recommendation": "How to fix"
    }}
  ],
  "risk_assessment": "Overall assessment in 2-3 sentences",
  "is_honeypot": true/false,
  "key_risks": ["risk1", "risk2"]
}}

Focus on:
1. Hidden mint/burn functions with owner-only access
2. Honeypot patterns (sell restrictions, blacklist abuse)
3. Proxy upgrade risks (no timelock, centralization)
4. Reentrancy in transfer/approve functions
5. Fee manipulation vectors
6. Unchecked external calls
7. tx.origin authentication
8. Storage collision in proxies

Only report genuine vulnerabilities. Do not flag standard ERC-20 patterns as issues."""


class LLMAnalyzer:
    """Uses LLM for intelligent contract analysis beyond static rules."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = requests.Session()

    def analyze(self, data: ContractData, rule_result: AuditResult) -> AuditResult:
        """Enhance rule-based results with LLM analysis."""
        if not data.source_code:
            logger.warning("No source code available for LLM analysis")
            return rule_result

        prompt = ANALYSIS_PROMPT.format(
            address=data.address,
            chain=data.chain,
            compiler=data.compiler_version or "unknown",
            is_proxy=data.is_proxy,
            implementation=data.implementation_address or "N/A",
            functions="\n".join(data.all_functions[:50]),
            source=data.source_code[:8000],
        )

        try:
            response = self._call_llm(prompt)
            findings = self._parse_response(response)

            for f in findings:
                rule_result.add_finding(f)

            # Recalculate score with LLM findings
            rule_result.risk_score = self._recalculate_score(rule_result)
            rule_result.summary = self._regenerate_summary(rule_result)

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")

        return rule_result

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API based on provider config."""
        provider = self.config.provider.lower()

        if provider == "claude":
            return self._call_anthropic(prompt)
        elif provider == "mimo":
            return self._call_mimo(prompt)
        elif provider == "deepseek":
            return self._call_deepseek(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _call_anthropic(self, prompt: str) -> str:
        """Call Claude API."""
        resp = self.session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.config.model or "claude-sonnet-4-20250514",
                "max_tokens": self.config.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    def _call_mimo(self, prompt: str) -> str:
        """Call Xiaomi MiMo API."""
        base_url = self.config.base_url or "https://api.xiaomimimo.com/v1"
        resp = self.session.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model or "MiMo-7B-RL",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek API."""
        resp = self.session.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model or "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _parse_response(self, response: str) -> list[Finding]:
        """Parse LLM JSON response into Finding objects."""
        # Extract JSON from response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            logger.warning("No JSON found in LLM response")
            return []

        try:
            data = json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response")
            return []

        findings = []
        risk_map = {
            "critical": RiskLevel.CRITICAL,
            "high": RiskLevel.HIGH,
            "medium": RiskLevel.MEDIUM,
            "low": RiskLevel.LOW,
        }

        for item in data.get("findings", []):
            findings.append(
                Finding(
                    rule_id=item.get("rule_id", "LLM-000"),
                    title=item.get("title", "LLM Finding"),
                    description=item.get("description", ""),
                    risk=risk_map.get(item.get("risk", "medium"), RiskLevel.MEDIUM),
                    confidence=float(item.get("confidence", 0.7)),
                    recommendation=item.get("recommendation", ""),
                )
            )

        return findings

    def _recalculate_score(self, result: AuditResult) -> int:
        """Recalculate risk score including LLM findings."""
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

    def _regenerate_summary(self, result: AuditResult) -> str:
        """Regenerate summary with updated findings."""
        counts = {}
        for f in result.findings:
            counts[f.risk.value] = counts.get(f.risk.value, 0) + 1
        parts = [f"{count} {level.upper()}" for level, count in counts.items() if count > 0]
        return f"Risk Score: {result.risk_score}/100 ({result.risk_level}) — Findings: {', '.join(parts) if parts else 'None'}"
