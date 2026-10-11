// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";

/// @title ProvenanceRegistry — append-only mint/transfer event log.
/// @notice Cheap verifiability layer. In Nepal fiat mode the equivalent is the
///         SIGNED off-chain provenance log (same event shape, platform-signed).
/// @notice Stores hashes only — never analytics, coordinates, or personal data.
contract ProvenanceRegistry is AccessControl {
    bytes32 public constant RECORDER_ROLE = keccak256("RECORDER_ROLE");

    struct Record {
        bytes32 assetId;
        bytes32 manifestHash;
        address from;
        address to;
        bytes32 ref; // tx ref / registry signature
        uint64 recordedAt;
        string kind; // "mint" | "transfer" | "auction_settled"
    }

    Record[] public records;
    mapping(bytes32 => uint256[]) private _byAsset;

    event ProvenanceRecorded(uint256 indexed index, bytes32 indexed assetId, string kind);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(RECORDER_ROLE, msg.sender);
    }

    function record(
        bytes32 assetId,
        bytes32 manifestHash,
        address from,
        address to,
        bytes32 ref,
        string calldata kind
    ) external onlyRole(RECORDER_ROLE) returns (uint256) {
        records.push(
            Record({
                assetId: assetId,
                manifestHash: manifestHash,
                from: from,
                to: to,
                ref: ref,
                recordedAt: uint64(block.timestamp),
                kind: kind
            })
        );
        uint256 index = records.length - 1;
        _byAsset[assetId].push(index);
        emit ProvenanceRecorded(index, assetId, kind);
        return index;
    }

    function recordsFor(bytes32 assetId) external view returns (uint256[] memory) {
        return _byAsset[assetId];
    }
}
