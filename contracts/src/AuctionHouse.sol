// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

interface INexusInsight {
    function transferRestricted(bytes32 assetId, address to, bytes32 settlementRef) external;
    function ownerOf(uint256 tokenId) external view returns (address);
}

/// @title AuctionHouse — English auctions for insight assets (on-chain rail).
/// @notice Used ONLY where crypto settlement is legally cleared. Nepal production
///         uses the fiat rail (SettlementAdapter) instead.
/// @notice Invariants: atomic settle (payment + fee + transfer or nothing);
///         expired/cancelled auctions cannot settle; escrow never double-spent.
contract AuctionHouse is AccessControl, ReentrancyGuard, Pausable {
    bytes32 public constant AUCTIONEER_ROLE = keccak256("AUCTIONEER_ROLE");

    struct Auction {
        bytes32 assetId;
        address seller;
        uint64 endsAt;
        uint256 reserve;
        uint256 highBid;
        address highBidder;
        bool settled;
        bool cancelled;
    }

    INexusInsight public immutable insight;
    address public immutable feeRecipient;
    uint256 public immutable feeBps; // e.g. 500 = 5%

    mapping(bytes32 => Auction) public auctions;
    /// auctionId => bidder => escrowed amount
    mapping(bytes32 => mapping(address => uint256)) public escrow;

    event AuctionCreated(bytes32 indexed auctionId, bytes32 indexed assetId, uint64 endsAt, uint256 reserve);
    event BidPlaced(bytes32 indexed auctionId, address indexed bidder, uint256 amount);
    event AuctionExtended(bytes32 indexed auctionId, uint64 newEndsAt);
    event AuctionSettled(bytes32 indexed auctionId, bytes32 indexed assetId, address winner, uint256 amount);
    event AuctionCancelled(bytes32 indexed auctionId);
    event Refunded(bytes32 indexed auctionId, address indexed bidder, uint256 amount);

    error UnknownAuction();
    error AuctionEnded();
    error AuctionNotEnded();
    error BidTooLow();
    error ReserveNotMet();
    error AlreadySettled();
    error NothingToRefund();

    uint64 public constant ANTI_SNIPE_WINDOW = 10 minutes;

    constructor(address _insight, address _feeRecipient, uint256 _feeBps) {
        insight = INexusInsight(_insight);
        feeRecipient = _feeRecipient;
        feeBps = _feeBps;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(AUCTIONEER_ROLE, msg.sender);
    }

    function createAuction(
        bytes32 auctionId,
        bytes32 assetId,
        uint64 endsAt,
        uint256 reserve
    ) external onlyRole(AUCTIONEER_ROLE) whenNotPaused {
        require(auctions[auctionId].seller == address(0), "exists");
        require(endsAt > block.timestamp, "bad endsAt");
        auctions[auctionId] = Auction({
            assetId: assetId,
            seller: msg.sender,
            endsAt: endsAt,
            reserve: reserve,
            highBid: 0,
            highBidder: address(0),
            settled: false,
            cancelled: false
        });
        emit AuctionCreated(auctionId, assetId, endsAt, reserve);
    }

    /// @notice Place a bid, escrowing native currency. Must beat high bid.
    function placeBid(bytes32 auctionId) external payable nonReentrant whenNotPaused {
        Auction storage a = auctions[auctionId];
        if (a.seller == address(0)) revert UnknownAuction();
        if (a.cancelled || a.settled || block.timestamp >= a.endsAt) revert AuctionEnded();
        uint256 minBid = a.highBid == 0 ? a.reserve : (a.highBid * 105) / 100; // 5% increment
        if (msg.value < minBid) revert BidTooLow();

        // refund previous high bidder's escrow accounting (pull pattern via escrow map)
        if (a.highBidder != address(0)) {
            escrow[auctionId][a.highBidder] += a.highBid;
        }
        a.highBid = msg.value;
        a.highBidder = msg.sender;

        // anti-sniping: bid in the last window extends the auction
        if (a.endsAt - block.timestamp < ANTI_SNIPE_WINDOW) {
            a.endsAt = uint64(block.timestamp + ANTI_SNIPE_WINDOW);
            emit AuctionExtended(auctionId, a.endsAt);
        }
        emit BidPlaced(auctionId, msg.sender, msg.value);
    }

    /// @notice Withdraw escrowed funds (outbid bidders pull their own refunds).
    function withdrawRefund(bytes32 auctionId) external nonReentrant {
        uint256 amount = escrow[auctionId][msg.sender];
        if (amount == 0) revert NothingToRefund();
        escrow[auctionId][msg.sender] = 0;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "refund failed");
        emit Refunded(auctionId, msg.sender, amount);
    }

    /// @notice Atomic settle: fee + seller payout + restricted token transfer.
    function settle(bytes32 auctionId) external nonReentrant whenNotPaused {
        Auction storage a = auctions[auctionId];
        if (a.seller == address(0)) revert UnknownAuction();
        if (a.settled || a.cancelled) revert AlreadySettled();
        if (block.timestamp < a.endsAt) revert AuctionNotEnded();
        if (a.highBid < a.reserve) revert ReserveNotMet();
        a.settled = true;

        uint256 fee = (a.highBid * feeBps) / 10_000;
        (bool okFee, ) = feeRecipient.call{value: fee}("");
        require(okFee, "fee failed");
        (bool okSeller, ) = a.seller.call{value: a.highBid - fee}("");
        require(okSeller, "payout failed");

        bytes32 settlementRef = keccak256(abi.encodePacked(auctionId, a.highBidder, a.highBid));
        insight.transferRestricted(a.assetId, a.highBidder, settlementRef);
        emit AuctionSettled(auctionId, a.assetId, a.highBidder, a.highBid);
    }

    function cancel(bytes32 auctionId) external {
        Auction storage a = auctions[auctionId];
        if (a.seller == address(0)) revert UnknownAuction();
        require(msg.sender == a.seller || hasRole(AUCTIONEER_ROLE, msg.sender), "not seller");
        require(a.highBidder == address(0), "bids placed");
        require(!a.settled, "settled");
        a.cancelled = true;
        emit AuctionCancelled(auctionId);
    }
}
