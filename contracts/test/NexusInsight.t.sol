// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/NexusInsight.sol";

contract NexusInsightTest is Test {
    NexusInsight insight;
    address creator = address(0xC4EA704);
    address buyer = address(0xB0E4);

    bytes32 assetId = keccak256("asset-1");
    bytes32 manifest = keccak256("manifest-1");

    function setUp() public {
        insight = new NexusInsight();
        insight.grantRole(insight.SETTLER_ROLE(), address(this));
    }

    function test_mint_records_manifest() public {
        insight.mint(assetId, creator, manifest, "ipfs://meta/1");
        assertEq(insight.manifestOf(assetId), manifest);
        assertEq(insight.ownerOf(uint256(assetId)), creator);
    }

    function test_double_mint_reverts() public {
        insight.mint(assetId, creator, manifest, "ipfs://meta/1");
        vm.expectRevert(abi.encodeWithSelector(NexusInsight.AssetAlreadyMinted.selector, assetId));
        insight.mint(assetId, creator, manifest, "ipfs://meta/1");
    }

    function test_user_transfer_blocked() public {
        insight.mint(assetId, creator, manifest, "ipfs://meta/1");
        vm.prank(creator);
        vm.expectRevert(NexusInsight.TransferNotAllowed.selector);
        insight.transferFrom(creator, buyer, uint256(assetId));
    }

    function test_restricted_transfer_moves_token() public {
        insight.mint(assetId, creator, manifest, "ipfs://meta/1");
        insight.transferRestricted(assetId, buyer, keccak256("settle-1"));
        assertEq(insight.ownerOf(uint256(assetId)), buyer);
    }
}
