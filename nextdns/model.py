"""Type definitions for NextDNS."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnalyticsStatus:
    """AnalyticsStatus class."""

    default_queries: int = 0
    blocked_queries: int = 0
    allowed_queries: int = 0
    all_queries: int = 0
    blocked_queries_ratio: float = 0

    def __post_init__(self) -> None:
        """Call after initialization."""
        self.all_queries = sum(
            [self.default_queries, self.blocked_queries, self.allowed_queries]
        )

        self.blocked_queries_ratio = (
            0
            if not self.all_queries
            else round(self.blocked_queries / self.all_queries * 100, 1)
        )


@dataclass
class AnalyticsDnssec:
    """AnalyticsDnssec class."""

    not_validated_queries: int = 0
    validated_queries: int = 0
    validated_queries_ratio: float = 0

    def __post_init__(self) -> None:
        """Call after initialization."""
        all_queries = sum([self.validated_queries, self.not_validated_queries])

        self.validated_queries_ratio = (
            0
            if not all_queries
            else round(self.validated_queries / all_queries * 100, 1)
        )


@dataclass
class AnalyticsEncrypted:
    """AnalyticsEncrypted class."""

    encrypted_queries: int = 0
    unencrypted_queries: int = 0
    encrypted_queries_ratio: float = 0

    def __post_init__(self) -> None:
        """Call after initialization."""
        all_queries = sum([self.encrypted_queries, self.unencrypted_queries])

        self.encrypted_queries_ratio = (
            0
            if not all_queries
            else round(self.encrypted_queries / all_queries * 100, 1)
        )


@dataclass
class AnalyticsIpVersions:
    """AnalyticsIpVersions class."""

    ipv6_queries: int = 0
    ipv4_queries: int = 0
    ipv6_queries_ratio: float = 0

    def __post_init__(self) -> None:
        """Call after initialization."""
        all_queries = sum([self.ipv6_queries, self.ipv4_queries])

        self.ipv6_queries_ratio = (
            0 if not all_queries else round(self.ipv6_queries / all_queries * 100, 1)
        )


@dataclass
class AnalyticsProtocols:
    """AnalyticsProtocols class."""

    doh_queries: int = 0
    dot_queries: int = 0
    udp_queries: int = 0
    doh_queries_ratio: float = 0
    dot_queries_ratio: float = 0
    udp_queries_ratio: float = 0

    def __post_init__(self) -> None:
        """Call after initialization."""
        all_queries = sum([self.doh_queries, self.dot_queries, self.udp_queries])

        self.doh_queries_ratio = (
            0 if not all_queries else round(self.doh_queries / all_queries * 100, 1)
        )
        self.dot_queries_ratio = (
            0 if not all_queries else round(self.dot_queries / all_queries * 100, 1)
        )
        self.udp_queries_ratio = (
            0 if not all_queries else round(self.udp_queries / all_queries * 100, 1)
        )


@dataclass
class AllAnalytics:
    """AllAnalytics class."""

    dnssec: AnalyticsDnssec
    encrypted: AnalyticsEncrypted
    ip_versions: AnalyticsIpVersions
    protocols: AnalyticsProtocols
    status: AnalyticsStatus


@dataclass
class Profile:
    """Profile class."""

    allowlist: list
    denylist: list
    fingerprint: str
    id: str
    name: str
    parental_control: dict
    privacy: dict
    rewrites: list
    security: dict
    settings: dict
    setup: dict


@dataclass
class ProfileInfo:
    """ProfileInfo class."""

    id: str
    fingerprint: str
    name: str


@dataclass
class ConnectionStatus:
    """ConnectionStatus class."""

    connected: bool
    profile: str | None = None
