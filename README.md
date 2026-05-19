# Smart Contract Auditor Agent

AI-Powered Smart Contract Security Auditor built with multi-agent architecture. Automatically scans EVM smart contracts for honeypot patterns, suspicious proxy configurations, hidden mint functions, and common vulnerability patterns.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Orchestrator Agent                  │
│         (Claude / MiMo / DeepSeek)              │
│  Decomposes audit goals → coordinates subagents  │
└────────────┬────────────────┬────────────────────┘
             │                │
    ┌────────▼──────┐  ┌─────▼──────────┐
    │ Scanner Agent │  │ Analysis Agent  │
    │  (EVM RPC +   │  │  (LLM-powered  │
    │  Etherscan)   │  │  pattern match) │
    └────────┬──────┘  └─────┬──────────┘
             │                │
    ┌────────▼───────────────▼────────────┐
    │          Report Generator           │
    │  (Markdown / JSON / PDF output)     │
    └─────────────────────────────────────┘
```

## Features

- **Honeypot Detection**: Identifies contracts that allow buying but prevent/restrict selling
- **Proxy Analysis**: Detects upgradeable proxies without timelock, admin key risks
- **Hidden Mint**: Finds privileged mint functions accessible by owner/admin
- **Reentrancy Patterns**: Static analysis for common reentrancy vulnerabilities
- **Ownership Risks**: Flags excessive owner privileges, absent renounce mechanisms
- **Multi-LLM Support**: Uses Claude, MiMo, or DeepSeek for intelligent pattern analysis
- **Batch Scanning**: Queue and scan multiple contracts in parallel
- **Report Generation**: Structured Markdown/JSON audit reports with risk scores

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run single contract audit
python -m auditor scan 0xContractAddress --chain ethereum

# Batch scan from file
python -m auditor batch contracts.txt --output reports/

# Generate summary report
python -m auditor report reports/ --format markdown
```

## Supported Chains

| Chain | RPC | Explorer |
|-------|-----|----------|
| Ethereum | `eth-mainnet` | Etherscan |
| Arbitrum | `arb-mainnet` | Arbiscan |
| Optimism | `op-mainnet` | Optimistic Etherscan |
| Base | `base-mainnet` | Basescan |
| BSC | `bsc-mainnet` | BscScan |
| Polygon | `polygon-mainnet` | Polygonscan |

## Risk Scoring

| Score | Level | Description |
|-------|-------|-------------|
| 90-100 | CRITICAL | Immediate rug pull risk — do not interact |
| 70-89 | HIGH | Significant security concerns |
| 40-69 | MEDIUM | Potential risks, review recommended |
| 0-39 | LOW | No significant issues found |

## Tech Stack

- **Runtime**: Python 3.11+
- **LLM Providers**: Claude (Anthropic), MiMo (Xiaomi), DeepSeek
- **Blockchain**: web3.py, Etherscan API
- **Analysis**: Slither (static), custom pattern matching
- **Output**: Markdown, JSON, PDF (via WeasyPrint)

## Project Structure

```
smart-contract-auditor/
├── auditor/
│   ├── __init__.py
│   ├── agent.py          # Main orchestrator agent
│   ├── scanner.py        # EVM contract scanner
│   ├── analyzer.py       # LLM-powered analysis
│   ├── rules.py          # Detection rule engine
│   ├── report.py         # Report generator
│   ├── config.py         # Configuration management
│   └── chains.py         # Multi-chain RPC config
├── examples/
│   ├── honeypot.sol      # Example honeypot contract
│   ├── proxy_risk.sol    # Example risky proxy
│   └── sample_report.md  # Example audit report
├── tests/
│   ├── test_scanner.py
│   ├── test_analyzer.py
│   └── test_rules.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## License

MIT
