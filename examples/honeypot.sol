// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// EXAMPLE: Honeypot contract with hidden mint + sell restriction
// This is for educational/testing purposes only.

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract HoneypotExample is ERC20, Ownable {
    mapping(address => bool) private _isBlacklisted;
    bool private _tradingEnabled = false;
    uint256 public maxTxAmount;
    uint256 public sellFee = 10; // 10% sell fee

    constructor() ERC20("HoneypotToken", "HPT") {
        maxTxAmount = totalSupply() / 100; // 1% max tx
    }

    // Hidden mint — owner can mint unlimited tokens
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    // Trading must be enabled by owner
    function enableTrading() external onlyOwner {
        _tradingEnabled = true;
    }

    // Blacklist mechanism
    function blacklist(address account) external onlyOwner {
        _isBlacklisted[account] = true;
    }

    // Transfer hook — honeypot pattern
    function _transfer(
        address from,
        address to,
        uint256 amount
    ) internal override {
        require(_tradingEnabled, "Trading not enabled");
        require(!_isBlacklisted[from], "Sender blacklisted");
        require(!_isBlacklisted[to], "Receiver blacklisted");

        // Only owner can exceed max tx amount
        if (from != owner() && to != owner()) {
            require(amount <= maxTxAmount, "Exceeds max tx amount");
        }

        // Sell fee — only applies when selling (not buying)
        uint256 fee = 0;
        if (to != owner()) {
            fee = (amount * sellFee) / 100;
        }

        super._transfer(from, to, amount - fee);
        if (fee > 0) {
            super._transfer(from, owner(), fee);
        }
    }
}
