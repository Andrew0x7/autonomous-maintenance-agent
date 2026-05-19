"""Tests for the scanner module."""

import pytest
from unittest.mock import patch, MagicMock
from auditor.scanner import ContractScanner, ContractData


@pytest.fixture
def mock_chain_config():
    from auditor.config import ChainConfig
    return ChainConfig(
        name="ethereum",
        chain_id=1,
        rpc_url="https://eth.llamarpc.com",
        explorer_api="https://api.etherscan.io/api",
        explorer_key="test_key",
    )


def test_contract_data_defaults():
    data = ContractData(address="0x123", chain="ethereum")
    assert data.address == "0x123"
    assert data.chain == "ethereum"
    assert data.is_proxy is False
    assert data.implementation_address is None
    assert data.all_functions == []


def test_contract_data_with_source():
    data = ContractData(
        address="0x123",
        chain="ethereum",
        source_code="contract Test {}",
        is_proxy=True,
        implementation_address="0xabc",
    )
    assert data.is_proxy is True
    assert data.implementation_address == "0xabc"


def test_parse_abi():
    data = ContractData(
        address="0x123",
        chain="ethereum",
        abi='[{"type":"function","name":"transfer","inputs":[{"type":"address"},{"type":"uint256"}]},{"type":"event","name":"Transfer"}]',
    )
    scanner = ContractScanner.__new__(ContractScanner)
    scanner._parse_abi(data)
    assert "transfer(address,uint256)" in data.all_functions
    assert "Transfer" in data.events
