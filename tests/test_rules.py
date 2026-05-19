"""Tests for the rule engine."""

import pytest
from auditor.rules import RuleEngine, RiskLevel
from auditor.scanner import ContractData


@pytest.fixture
def engine():
    return RuleEngine()


@pytest.fixture
def honeypot_source():
    return """
    contract Honeypot is ERC20, Ownable {
        mapping(address => bool) private isBlack;
        bool trading = false;
        uint256 public sellFee = 10;

        function mint(address to, uint256 amount) external onlyOwner {
            _mint(to, amount);
        }

        function _transfer(address from, address to, uint256 amount) internal override {
            require(!isBlack[from]);
            require(trading);
            super._transfer(from, to, amount);
        }
    }
    """


def test_hidden_mint_detection(engine, honeypot_source):
    data = ContractData(address="0x123", chain="ethereum", source_code=honeypot_source)
    result = engine.evaluate(data)
    mint_findings = [f for f in result.findings if "MINT" in f.rule_id]
    assert len(mint_findings) >= 1
    assert mint_findings[0].risk in (RiskLevel.CRITICAL, RiskLevel.HIGH)


def test_honeypot_detection(engine, honeypot_source):
    data = ContractData(address="0x123", chain="ethereum", source_code=honeypot_source)
    result = engine.evaluate(data)
    honeypot_findings = [f for f in result.findings if "HONEYPOT" in f.rule_id]
    assert len(honeypot_findings) >= 1


def test_blacklist_detection(engine, honeypot_source):
    data = ContractData(address="0x123", chain="ethereum", source_code=honeypot_source)
    result = engine.evaluate(data)
    blacklist_findings = [f for f in result.findings if "BLACKLIST" in f.rule_id]
    assert len(blacklist_findings) >= 1


def test_clean_contract(engine):
    clean_source = """
    contract Clean is ERC20 {
        constructor() ERC20("Clean", "CLN") {
            _mint(msg.sender, 1000000 * 10**18);
        }
    }
    """
    data = ContractData(address="0x456", chain="ethereum", source_code=clean_source)
    result = engine.evaluate(data)
    assert result.risk_score < 40
    assert result.risk_level == "LOW"


def test_proxy_no_timelock(engine):
    data = ContractData(
        address="0x789",
        chain="ethereum",
        source_code="contract Proxy {}",
        is_proxy=True,
        implementation_address="0xabc",
    )
    result = engine.evaluate(data)
    proxy_findings = [f for f in result.findings if "PROXY" in f.rule_id]
    assert len(proxy_findings) >= 1
    assert proxy_findings[0].risk == RiskLevel.HIGH


def test_selfdestruct_detection(engine):
    source = """
    contract Dangerous {
        function destroy() external {
            selfdestruct(payable(msg.sender));
        }
    }
    """
    data = ContractData(address="0xdef", chain="ethereum", source_code=source)
    result = engine.evaluate(data)
    destroy_findings = [f for f in result.findings if "DESTRUCT" in f.rule_id]
    assert len(destroy_findings) >= 1
    assert destroy_findings[0].risk == RiskLevel.HIGH


def test_tx_origin_detection(engine):
    source = """
    contract TxOrigin {
        function login() external {
            require(tx.origin == owner());
        }
    }
    """
    data = ContractData(address="0x111", chain="ethereum", source_code=source)
    result = engine.evaluate(data)
    tx_findings = [f for f in result.findings if "TXORIGIN" in f.rule_id]
    assert len(tx_findings) >= 1


def test_risk_score_capped(engine):
    """Risk score should never exceed 100."""
    source = """
    contract MegaRisk is Ownable {
        mapping(address => bool) private isBlack;
        function mint() external onlyOwner {}
        function mint2() external onlyOwner {}
        function mint3() external onlyOwner {}
        function destroy() external { selfdestruct(payable(msg.sender)); }
        function login() external { require(tx.origin == owner()); }
        assembly { let x := 1 }
        assembly { let y := 2 }
        assembly { let z := 3 }
        assembly { let w := 4 }
    }
    """
    data = ContractData(address="0x999", chain="ethereum", source_code=source)
    result = engine.evaluate(data)
    assert result.risk_score <= 100
