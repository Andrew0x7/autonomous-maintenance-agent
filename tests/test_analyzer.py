"""Tests for the LLM analyzer."""

import pytest
from unittest.mock import patch, MagicMock
from auditor.analyzer import LLMAnalyzer
from auditor.config import LLMConfig
from auditor.scanner import ContractData
from auditor.rules import AuditResult, RuleEngine


@pytest.fixture
def analyzer():
    config = LLMConfig(provider="mimo", api_key="test_key", base_url="http://localhost:8000/v1")
    return LLMAnalyzer(config)


@pytest.fixture
def sample_contract():
    return ContractData(
        address="0x123",
        chain="ethereum",
        source_code="contract Test { function mint() external {} }",
        compiler_version="v0.8.19",
    )


@pytest.fixture
def sample_result(sample_contract):
    return AuditResult(contract=sample_contract)


def test_parse_valid_json(analyzer):
    response = '''
    {
        "findings": [
            {
                "rule_id": "LLM-001",
                "title": "Test Finding",
                "description": "Test description",
                "risk": "high",
                "confidence": 0.85,
                "recommendation": "Fix this"
            }
        ],
        "risk_assessment": "High risk contract",
        "is_honeypot": true,
        "key_risks": ["hidden mint"]
    }
    '''
    findings = analyzer._parse_response(response)
    assert len(findings) == 1
    assert findings[0].rule_id == "LLM-001"
    assert findings[0].risk.value == "high"
    assert findings[0].confidence == 0.85


def test_parse_invalid_json(analyzer):
    findings = analyzer._parse_response("not json at all")
    assert findings == []


def test_parse_missing_fields(analyzer):
    response = '{"findings": [{"title": "test"}]}'
    findings = analyzer._parse_response(response)
    assert len(findings) == 1
    assert findings[0].rule_id == "LLM-000"  # default
    assert findings[0].risk.value == "medium"  # default
