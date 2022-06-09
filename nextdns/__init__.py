"""Python wrapper for NextDNS API."""
from __future__ import annotations

import logging
from collections.abc import Iterable
from http import HTTPStatus
from typing import Any

from aiohttp import ClientSession

from .const import (
    ATTR_ANALYTICS,
    ATTR_PROFILE,
    ATTR_PROFILES,
    DNSSEC_MAP,
    ENCRYPTED_MAP,
    ENDPOINTS,
    IP_VERSIONS_MAP,
    PROTOCOLS_MAP,
    STATUS_MAP,
)
from .exceptions import ApiError, InvalidApiKeyError
from .model import (
    AnalyticsDnssec,
    AnalyticsEncrypted,
    AnalyticsIpVersions,
    AnalyticsProtocols,
    AnalyticsStatus,
    Profile,
)

_LOGGER = logging.getLogger(__name__)


class NextDns:
    """Main class of NextDNS API wrapper."""

    def __init__(self, session: ClientSession, api_key: str) -> None:
        """Initialize NextDNS API wrapper."""
        self._session = session
        self._headers = {"X-Api-Key": api_key}
        self._api_key = api_key
        self._profiles: Iterable[tuple[str, str]]

    @classmethod
    async def create(cls, session: ClientSession, api_key: str) -> NextDns:
        """Create a new instance."""
        instance = cls(session, api_key)
        await instance.initialize()
        return instance

    async def initialize(self) -> None:
        """Initialize."""
        _LOGGER.debug("Initializing with API Key: %s...", self._api_key[:10])
        self._profiles = self._parse_profiles(await self.get_profiles())

    async def get_profiles(self) -> list[dict[str, str]]:
        """Get all profiles."""
        url = ENDPOINTS[ATTR_PROFILES]
        return await self._http_request("get", url)

    async def get_profile(self, profile: str) -> dict[str, str]:
        """Get profile."""
        url = ENDPOINTS[ATTR_PROFILE].format(profile=profile)
        resp = await self._http_request("get", url)
        return Profile(**resp)

    async def get_analytics_status(self, profile: str) -> AnalyticsStatus:
        """Get profile analytics status."""
        url = ENDPOINTS[ATTR_ANALYTICS].format(profile=profile, type="status")
        resp = await self._http_request("get", url)
        return AnalyticsStatus(
            **{STATUS_MAP[item["status"]]: item["queries"] for item in resp}
        )

    async def get_analytics_dnssec(self, profile: str) -> AnalyticsDnssec:
        """Get profile analytics dnssec."""
        url = ENDPOINTS[ATTR_ANALYTICS].format(profile=profile, type="dnssec")
        resp = await self._http_request("get", url)
        return AnalyticsDnssec(
            **{DNSSEC_MAP[item["validated"]]: item["queries"] for item in resp}
        )

    async def get_analytics_encryption(self, profile: str) -> AnalyticsEncrypted:
        """Get profile analytics encryption."""
        url = ENDPOINTS[ATTR_ANALYTICS].format(profile=profile, type="encryption")
        resp = await self._http_request("get", url)
        return AnalyticsEncrypted(
            **{ENCRYPTED_MAP[item["encrypted"]]: item["queries"] for item in resp}
        )

    async def get_analytics_ip_versions(self, profile: str) -> AnalyticsIpVersions:
        """Get profile analytics IP versions."""
        url = ENDPOINTS[ATTR_ANALYTICS].format(profile=profile, type="ipVersions")
        resp = await self._http_request("get", url)
        return AnalyticsIpVersions(
            **{IP_VERSIONS_MAP[item["version"]]: item["queries"] for item in resp}
        )

    async def get_analytics_protocols(self, profile: str) -> AnalyticsProtocols:
        """Get profile analytics protocols."""
        url = ENDPOINTS[ATTR_ANALYTICS].format(profile=profile, type="protocols")
        resp = await self._http_request("get", url)
        return AnalyticsProtocols(
            **{PROTOCOLS_MAP[item["protocol"]]: item["queries"] for item in resp}
        )

    async def _http_request(self, method: str, url: str) -> Any:
        """Retrieve data from the device."""
        _LOGGER.debug("Requesting %s, method: %s", url, method)

        resp = await self._session.request(method, url, headers=self._headers)

        _LOGGER.debug("Response status: %s", resp.status)

        if resp.status == HTTPStatus.FORBIDDEN.value:
            raise InvalidApiKeyError
        if resp.status != HTTPStatus.OK.value:
            result = await resp.json()
            raise ApiError(f"{resp.status}, {result['errors'][0]['code']}")

        result = await resp.json()
        _LOGGER.debug("Response result: %s", result)
        return result["data"]

    @staticmethod
    def _parse_profiles(profiles: list[dict[str, str]]) -> Iterable[tuple[str, str]]:
        """Parse profiles."""
        for profile in profiles:
            yield profile["id"], profile["name"]

    @property
    def profiles(self) -> list[tuple[str, str]]:
        """Return profiles."""
        return list(self._profiles)
