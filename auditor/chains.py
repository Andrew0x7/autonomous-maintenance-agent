"""
Multi-chain RPC and explorer configuration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChainInfo:
    name: str
    chain_id: int
    native_token: str
    rpc_endpoints: list[str]
    explorer_api: str
    explorer_url: str


# Supported chains
CHAINS: dict[str, ChainInfo] = {
    "ethereum": ChainInfo(
        name="Ethereum",
        chain_id=1,
        native_token="ETH",
        rpc_endpoints=[
            "https://eth.llamarpc.com",
            "https://rpc.ankr.com/eth",
            "https://ethereum.publicnode.com",
        ],
        explorer_api="https://api.etherscan.io/api",
        explorer_url="https://etherscan.io",
    ),
    "arbitrum": ChainInfo(
        name="Arbitrum One",
        chain_id=42161,
        native_token="ETH",
        rpc_endpoints=[
            "https://arb1.arbitrum.io/rpc",
            "https://rpc.ankr.com/arbitrum",
        ],
        explorer_api="https://api.arbiscan.io/api",
        explorer_url="https://arbiscan.io",
    ),
    "optimism": ChainInfo(
        name="Optimism",
        chain_id=10,
        native_token="ETH",
        rpc_endpoints=[
            "https://mainnet.optimism.io",
            "https://rpc.ankr.com/optimism",
        ],
        explorer_api="https://api-optimistic.etherscan.io/api",
        explorer_url="https://optimistic.etherscan.io",
    ),
    "base": ChainInfo(
        name="Base",
        chain_id=8453,
        native_token="ETH",
        rpc_endpoints=[
            "https://mainnet.base.org",
            "https://rpc.ankr.com/base",
        ],
        explorer_api="https://api.basescan.org/api",
        explorer_url="https://basescan.org",
    ),
    "bsc": ChainInfo(
        name="BNB Smart Chain",
        chain_id=56,
        native_token="BNB",
        rpc_endpoints=[
            "https://bsc-dataseed.binance.org",
            "https://rpc.ankr.com/bsc",
        ],
        explorer_api="https://api.bscscan.com/api",
        explorer_url="https://bscscan.com",
    ),
    "polygon": ChainInfo(
        name="Polygon",
        chain_id=137,
        native_token="MATIC",
        rpc_endpoints=[
            "https://polygon-rpc.com",
            "https://rpc.ankr.com/polygon",
        ],
        explorer_api="https://api.polygonscan.com/api",
        explorer_url="https://polygonscan.com",
    ),
}


def get_chain(name: str) -> Optional[ChainInfo]:
    """Get chain info by name."""
    return CHAINS.get(name.lower())


def list_chains() -> list[str]:
    """List supported chain names."""
    return list(CHAINS.keys())
