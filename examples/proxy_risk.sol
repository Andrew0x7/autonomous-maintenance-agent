// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// EXAMPLE: Upgradeable proxy with NO timelock — admin can upgrade instantly
// This is for educational/testing purposes only.

import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";

// Risky: No timelock, admin can upgrade at any time
contract RiskyProxy is TransparentUpgradeableProxy {
    constructor(
        address logic,
        address admin,
        bytes memory data
    ) TransparentUpgradeableProxy(logic, admin, data) {}
}

// Better: With timelock
// import "@openzeppelin/contracts/governance/TimelockController.sol";
// contract SafeProxy is TransparentUpgradeableProxy {
//     constructor(
//         address logic,
//         address admin, // TimelockController address
//         bytes memory data
//     ) TransparentUpgradeableProxy(logic, admin, data) {}
// }
