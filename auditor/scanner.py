"""
EVM Smart Contract Scanner.
Fetches bytecode, ABI, source code, and storage layout from blockchain + explorer APIs.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import requests
from web3 import Web3

from .config import ChainConfig

logger = logging.getLogger(__name__)


@dataclass
class ContractData:
    """Raw contract data fetched from chain + explorer."""
    address: str
    chain: str
    bytecode: str = ""
    source_code: str = ""
    abi: str = ""
    compiler_version: str = ""
    is_proxy: bool = False
    implementation_address: Optional[str] = None
    owner_address: Optional[str] = None
    creation_tx: Optional[str] = None
    storage_layout: dict = field(default_factory=dict)
    all_functions: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    raw_metadata: dict = field(default_factory=dict)


class ContractScanner:
    """Fetches contract data from EVM chain and block explorer."""

    # EIP-1967 proxy storage slots
    IMPLEMENTATION_SLOT = (
        "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
    )
    ADMIN_SLOT = (
        "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
    )

    def __init__(self, chain_config: ChainConfig):
        self.chain = chain_config
        self.w3 = Web3(Web3.HTTPProvider(chain_config.rpc_url))
        self.session = requests.Session()

    def scan(self, address: str) -> ContractData:
        """Full scan of a contract address."""
        address = Web3.to_checksum_address(address)
        logger.info(f"Scanning {address} on {self.chain.name}")

        data = ContractData(address=address, chain=self.chain.name)

        # Fetch bytecode
        data.bytecode = self.w3.eth.get_code(address).hex()

        # Fetch from explorer API
        self._fetch_explorer_data(data)

        # Check proxy patterns
        self._detect_proxy(data)

        # Parse functions and events from ABI
        self._parse_abi(data)

        return data

    def _fetch_explorer_data(self, data: ContractData):
        """Fetch source code, ABI, and metadata from block explorer."""
        if not self.chain.explorer_key:
            logger.warning(f"No explorer API key for {self.chain.name}")
            return

        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": data.address,
            "apikey": self.chain.explorer_key,
        }
        try:
            resp = self.session.get(
                self.chain.explorer_api, params=params, timeout=30
            )
            result = resp.json().get("result", [{}])[0]

            data.source_code = result.get("SourceCode", "")
            data.abi = result.get("ABI", "")
            data.compiler_version = result.get("CompilerVersion", "")
            data.raw_metadata = result

            if data.source_code.startswith("{{"):
                # Multi-file format
                data.source_code = data.source_code[1:-1]

        except Exception as e:
            logger.error(f"Explorer API error: {e}")

    def _detect_proxy(self, data: ContractData):
        """Detect EIP-1967 proxy patterns."""
        try:
            impl_slot = self.w3.eth.get_storage_at(
                data.address, int(self.IMPLEMENTATION_SLOT, 16)
            )
            impl_address = "0x" + impl_slot[-20:].hex()

            if impl_address != "0x" + "0" * 40:
                data.is_proxy = True
                data.implementation_address = Web3.to_checksum_address(impl_address)
                logger.info(f"Proxy detected → implementation: {impl_address}")

            admin_slot = self.w3.eth.get_storage_at(
                data.address, int(self.ADMIN_SLOT, 16)
            )
            admin_address = "0x" + admin_slot[-20:].hex()
            if admin_address != "0x" + "0" * 40:
                data.owner_address = Web3.to_checksum_address(admin_address)

        except Exception as e:
            logger.debug(f"Proxy detection failed: {e}")

    def _parse_abi(self, data: ContractData):
        """Parse functions and events from ABI JSON."""
        if not data.abi or data.abi == "Contract source code not verified":
            return

        try:
            abi = json.loads(data.abi) if isinstance(data.abi, str) else data.abi
            for item in abi:
                if item.get("type") == "function":
                    inputs = ",".join(
                        i.get("type", "") for i in item.get("inputs", [])
                    )
                    data.all_functions.append(f"{item['name']}({inputs})")
                elif item.get("type") == "event":
                    data.events.append(item["name"])
        except json.JSONDecodeError:
            logger.warning("Failed to parse ABI JSON")

    def get_bytecode_hash(self, data: ContractData) -> str:
        """Generate hash of bytecode for similarity matching."""
        import hashlib
        return hashlib.sha256(bytes.fromhex(data.bytecode[2:])).hexdigest()[:16]
