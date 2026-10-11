// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/// @title NexusInsight — transfer-restricted ERC-721 for insight assets.
/// @notice One token per post-popularity insight asset. tokenId = uint256(asset UUID).
/// @notice Transfers are RESTRICTED: only the AuctionHouse (via settle) or the
///         platform MINTER_ROLE can move tokens. This keeps off-chain entitlements,
///         KMS policies, and fee capture in sync. Arbitrary wallet-to-wallet
///         transfers are blocked by design.
/// @notice The chain stores commitments (assetId -> manifestHash), NEVER raw
///         analytics, coordinates, messages, or personal data.
contract NexusInsight is ERC721, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant SETTLER_ROLE = keccak256("SETTLER_ROLE");

    /// @notice assetId => sha256(ciphertext || metadata). Immutable once minted.
    mapping(bytes32 => bytes32) private _manifests;

    event AssetMinted(bytes32 indexed assetId, bytes32 manifestHash, address indexed creator);
    event AssetTransferred(
        bytes32 indexed assetId, address indexed from, address indexed to, bytes32 settlementRef
    );

    error AssetAlreadyMinted(bytes32 assetId);
    error UnknownAsset(bytes32 assetId);
    error TransferNotAllowed();

    constructor() ERC721("NexusInsight", "NXSI") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
    }

    /// @notice Mint the insight token. Callable only by the platform minter role.
    function mint(
        bytes32 assetId,
        address to,
        bytes32 manifestHash,
        string calldata metadataURI
    ) external onlyRole(MINTER_ROLE) {
        if (_manifests[assetId] != bytes32(0)) revert AssetAlreadyMinted(assetId);
        _manifests[assetId] = manifestHash;
        uint256 tokenId = uint256(assetId);
        _safeMint(to, tokenId);
        // metadataURI pinned off-chain; stored via _setTokenURI in full impl (ERC721URIStorage)
        metadataURI;
        emit AssetMinted(assetId, manifestHash, to);
    }

    /// @notice The immutable manifest commitment for an asset.
    function manifestOf(bytes32 assetId) external view returns (bytes32) {
        bytes32 m = _manifests[assetId];
        if (m == bytes32(0)) revert UnknownAsset(assetId);
        return m;
    }

    /// @notice Restricted transfer used ONLY by settlement (auction settle).
    function transferRestricted(
        bytes32 assetId,
        address to,
        bytes32 settlementRef
    ) external onlyRole(SETTLER_ROLE) {
        uint256 tokenId = uint256(assetId);
        address from = ownerOf(tokenId);
        _transfer(from, to, tokenId);
        emit AssetTransferred(assetId, from, to, settlementRef);
    }

    // ---- transfer restriction: block all user-initiated moves ----
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal override returns (address) {
        address from = _ownerOf(tokenId);
        // Allow mint (from == 0) and restricted settlement transfers (called by
        // transferRestricted under SETTLER_ROLE). Block everything else.
        if (from != address(0) && !hasRole(SETTLER_ROLE, msg.sender)) {
            revert TransferNotAllowed();
        }
        return super._update(to, tokenId, auth);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
