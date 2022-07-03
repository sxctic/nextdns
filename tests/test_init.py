"""Tests for nextdns package."""
import json
from http import HTTPStatus

import aiohttp
import pytest
from aioresponses import aioresponses

from nextdns import (
    ATTR_ANALYTICS,
    ATTR_CLEAR_LOGS,
    ATTR_PROFILE,
    ATTR_PROFILES,
    ATTR_TEST,
    ENDPOINTS,
    ApiError,
    InvalidApiKeyError,
    NextDns,
    ProfileIdNotFoundError,
    ProfileNameNotFoundError,
    SettingNotSupportedError,
)
from nextdns.const import ATTR_BLOCK_PAGE

PROFILE_ID = "fakepr"


@pytest.mark.asyncio
async def test_valid_data():  # pylint: disable=too-many-locals,too-many-statements
    """Test with valid data."""
    with open("tests/fixtures/profiles.json", encoding="utf-8") as file:
        profiles_data = json.load(file)
    with open("tests/fixtures/dnssec.json", encoding="utf-8") as file:
        dnssec_data = json.load(file)
    with open("tests/fixtures/encryption.json", encoding="utf-8") as file:
        encryption_data = json.load(file)
    with open("tests/fixtures/ip_versions.json", encoding="utf-8") as file:
        ip_versions_data = json.load(file)
    with open("tests/fixtures/protocols.json", encoding="utf-8") as file:
        protocols_data = json.load(file)
    with open("tests/fixtures/status.json", encoding="utf-8") as file:
        status_data = json.load(file)
    with open("tests/fixtures/test.json", encoding="utf-8") as file:
        test_data = json.load(file)
    with open("tests/fixtures/profile.json", encoding="utf-8") as file:
        profile_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], payload=profiles_data)
        session_mock.get(
            ENDPOINTS[ATTR_ANALYTICS].format(profile_id=PROFILE_ID, type="dnssec"),
            payload=dnssec_data,
        )
        session_mock.get(
            ENDPOINTS[ATTR_ANALYTICS].format(profile_id=PROFILE_ID, type="encryption"),
            payload=encryption_data,
        )
        session_mock.get(
            ENDPOINTS[ATTR_ANALYTICS].format(profile_id=PROFILE_ID, type="ipVersions"),
            payload=ip_versions_data,
        )
        session_mock.get(
            ENDPOINTS[ATTR_ANALYTICS].format(profile_id=PROFILE_ID, type="protocols"),
            payload=protocols_data,
        )
        session_mock.get(
            ENDPOINTS[ATTR_ANALYTICS].format(profile_id=PROFILE_ID, type="status"),
            payload=status_data,
        )
        session_mock.get(
            ENDPOINTS[ATTR_TEST].format(profile_id=PROFILE_ID), payload=test_data
        )
        session_mock.get(
            ENDPOINTS[ATTR_PROFILE].format(profile_id=PROFILE_ID), payload=profile_data
        )

        nextdns = await NextDns.create(session, "fakeapikey")

        analitycs = await nextdns.get_all_analytics(PROFILE_ID)
        dnssec = analitycs.dnssec
        encryption = analitycs.encryption
        ip_versions = analitycs.ip_versions
        protocols = analitycs.protocols
        status = analitycs.status
        connection_status = await nextdns.connection_status(PROFILE_ID)
        settings = await nextdns.get_settings(PROFILE_ID)

    await session.close()

    assert len(nextdns.profiles) == 1
    assert nextdns.profiles[0].id == PROFILE_ID
    assert nextdns.profiles[0].fingerprint == "fakeprofile12"
    assert nextdns.profiles[0].name == "Fake Profile"

    assert dnssec.not_validated_queries == 793765
    assert dnssec.validated_queries == 49451
    assert dnssec.validated_queries_ratio == 5.9

    assert encryption.encrypted_queries == 1380260
    assert encryption.unencrypted_queries == 40
    assert encryption.encrypted_queries_ratio == 100.0

    assert ip_versions.ipv6_queries == 42117
    assert ip_versions.ipv4_queries == 1338183
    assert ip_versions.ipv6_queries_ratio == 3.1

    assert protocols.doh_queries == 118488
    assert protocols.doq_queries == 0
    assert protocols.dot_queries == 1261772
    assert protocols.udp_queries == 40
    assert protocols.doh_queries_ratio == 8.6
    assert protocols.doq_queries_ratio == 0.0
    assert protocols.dot_queries_ratio == 91.4
    assert protocols.udp_queries_ratio == 0.0

    assert status.all_queries == 1380300
    assert status.allowed_queries == 5452
    assert status.blocked_queries == 530805
    assert status.default_queries == 837764
    assert status.relayed_queries == 6279
    assert status.blocked_queries_ratio == 38.5

    assert connection_status.connected is True
    assert connection_status.profile_id == PROFILE_ID

    assert settings.block_page is False
    assert settings.cache_boost is True
    assert settings.cname_flattening is True
    assert settings.anonymized_ecs is True
    assert settings.logs is True
    assert settings.web3 is True
    assert settings.allow_affiliate is True
    assert settings.block_disguised_trackers is True
    assert settings.ai_threat_detection is True
    assert settings.block_csam is True
    assert settings.block_ddns is True
    assert settings.block_nrd is True
    assert settings.block_parked_domains is True
    assert settings.cryptojacking_protection is True
    assert settings.dga_protection is True
    assert settings.dns_rebinding_protection is True
    assert settings.google_safe_browsing is True
    assert settings.idn_homograph_attacks_protection is True
    assert settings.threat_intelligence_feeds is True
    assert settings.typosquatting_protection is True
    assert settings.block_bypass_methods is True
    assert settings.safesearch is False
    assert settings.youtube_restricted_mode is False

    assert nextdns.get_profile_name(PROFILE_ID) == "Fake Profile"
    assert nextdns.get_profile_id("Fake Profile") == PROFILE_ID


@pytest.mark.asyncio
async def test_profile_id_not_found():
    """Test with wrong profile id."""
    with open("tests/fixtures/profiles.json", encoding="utf-8") as file:
        profiles_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], payload=profiles_data)

        nextdns = await NextDns.create(session, "fakeapikey")

    await session.close()

    try:
        nextdns.get_profile_name("xxyyxx")
    except Exception as exc:  # pylint: disable=broad-except
        assert isinstance(exc, ProfileIdNotFoundError) is True


@pytest.mark.asyncio
async def test_profile_name_not_found():
    """Test with wrong name id."""
    with open("tests/fixtures/profiles.json", encoding="utf-8") as file:
        profiles_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], payload=profiles_data)

        nextdns = await NextDns.create(session, "fakeapikey")

    await session.close()

    try:
        nextdns.get_profile_id("Profile Name")
    except Exception as exc:  # pylint: disable=broad-except
        assert isinstance(exc, ProfileNameNotFoundError) is True


@pytest.mark.asyncio
async def test_clear_logs():
    """Test clear_logs() method."""
    with open("tests/fixtures/profiles.json", encoding="utf-8") as file:
        profiles_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], payload=profiles_data)
        session_mock.delete(
            ENDPOINTS[ATTR_CLEAR_LOGS].format(profile_id=PROFILE_ID),
            status=HTTPStatus.NO_CONTENT.value,
        )

        nextdns = await NextDns.create(session, "fakeapikey")

        result = await nextdns.clear_logs(PROFILE_ID)

    await session.close()

    assert result is True


@pytest.mark.asyncio
async def test_set_setting():
    """Test set_setting() method."""
    with open("tests/fixtures/profiles.json", encoding="utf-8") as file:
        profiles_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], payload=profiles_data)
        session_mock.patch(
            ENDPOINTS[ATTR_BLOCK_PAGE].format(profile_id=PROFILE_ID),
            status=HTTPStatus.NO_CONTENT.value,
        )

        nextdns = await NextDns.create(session, "fakeapikey")

        result = await nextdns.set_setting(PROFILE_ID, "block_page", True)

    await session.close()

    assert result is True


@pytest.mark.asyncio
async def test_set_not_supported_setting():
    """Test set_setting() method with not supported setting."""
    with open("tests/fixtures/profiles.json", encoding="utf-8") as file:
        profiles_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], payload=profiles_data)

        nextdns = await NextDns.create(session, "fakeapikey")

        try:
            await nextdns.set_setting(PROFILE_ID, "unsupported_setting", True)
        except Exception as exc:  # pylint: disable=broad-except
            assert isinstance(exc, SettingNotSupportedError) is True

    await session.close()


@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test error when provided API key is invalid."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(ENDPOINTS[ATTR_PROFILES], status=HTTPStatus.FORBIDDEN.value)

        try:
            await NextDns.create(session, "fakeapikey")
        except Exception as exc:  # pylint: disable=broad-except
            assert isinstance(exc, InvalidApiKeyError) is True

    await session.close()


@pytest.mark.asyncio
async def test_api_error():
    """Test API error."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            ENDPOINTS[ATTR_PROFILES],
            status=HTTPStatus.BAD_REQUEST.value,
            payload={"errors": [{"code": "badRequest"}]},
        )

        try:
            await NextDns.create(session, "fakeapikey")
        except ApiError as exc:
            assert str(exc.status) == "400, badRequest"

    await session.close()
