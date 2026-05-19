"""
Configuration management for Smart Contract Auditor Agent.
Loads API keys and settings from environment / .env file.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "mimo"  # mimo, claude, deepseek
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    max_tokens: int = 4096
    temperature: float = 0.1

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY", "")


@dataclass
class ChainConfig:
    """Blockchain RPC configuration."""
    name: str
    chain_id: int
    rpc_url: str
    explorer_api: str
    explorer_key: str = ""

    def __post_init__(self):
        if not self.explorer_key:
            self.explorer_key = os.getenv(f"{self.name.upper()}_EXPLORER_KEY", "")


@dataclass
class AuditConfig:
    """Main audit configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    chains: dict[str, ChainConfig] = field(default_factory=dict)
    output_dir: str = "./reports"
    max_concurrent: int = 5
    timeout: int = 120
    enable_slither: bool = True

    @classmethod
    def from_env(cls, env_path: Optional[str] = None) -> "AuditConfig":
        """Load config from .env file and environment variables."""
        if env_path and Path(env_path).exists():
            _load_dotenv(env_path)

        config = cls()
        config.llm = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "mimo"),
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", ""),
            model=os.getenv("LLM_MODEL", ""),
        )
        config.output_dir = os.getenv("AUDIT_OUTPUT_DIR", "./reports")
        config.max_concurrent = int(os.getenv("AUDIT_MAX_CONCURRENT", "5"))
        config.timeout = int(os.getenv("AUDIT_TIMEOUT", "120"))
        config.enable_slither = os.getenv("ENABLE_SLITHER", "true").lower() == "true"

        # Load chain configs
        for chain_name, chain_id, default_rpc in CHAIN_DEFAULTS:
            rpc_env = f"{chain_name.upper()}_RPC_URL"
            explorer_env = f"{chain_name.upper()}_EXPLORER_KEY"
            config.chains[chain_name] = ChainConfig(
                name=chain_name,
                chain_id=chain_id,
                rpc_url=os.getenv(rpc_env, default_rpc),
                explorer_api=f"https://api.{chain_name}scan.com/api",
                explorer_key=os.getenv(explorer_env, ""),
            )
        return config


# Default chain configurations
CHAIN_DEFAULTS = [
    ("ethereum", 1, "https://eth.llamarpc.com"),
    ("arbitrum", 42161, "https://arb1.arbitrum.io/rpc"),
    ("optimism", 10, "https://mainnet.optimism.io"),
    ("base", 8453, "https://mainnet.base.org"),
    ("bsc", 56, "https://bsc-dataseed.binance.org"),
    ("polygon", 137, "https://polygon-rpc.com"),
]


def _load_dotenv(path: str):
    """Minimal .env loader."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
