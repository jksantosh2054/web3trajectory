"""Import all models here so Alembic autogenerate and Base.metadata see them."""
from app.models.assets import (  # noqa: F401
    AnalyticsSnapshot,
    Auction,
    Bid,
    Entitlement,
    InsightAsset,
    OwnershipTransfer,
)
from app.models.creator import EngagementEvent, Post, PostVersion  # noqa: F401
from app.models.dating import (  # noqa: F401
    Block,
    Conversation,
    DatePresence,
    DateProfile,
    DateProposal,
    Message,
)
from app.models.identity import (  # noqa: F401
    Profile,
    User,
    UserConsent,
    UserPreference,
    WalletLink,
)
from app.models.market import (  # noqa: F401
    InventoryReservation,
    Listing,
    Order,
    OrderItem,
    Payment,
    Product,
    Review,
    Seller,
)
from app.models.ops import AuditEvent, OutboxEvent, Report  # noqa: F401
