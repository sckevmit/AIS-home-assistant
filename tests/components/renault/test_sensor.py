"""Tests for Renault sensors."""
from unittest.mock import PropertyMock, patch

import pytest
from renault_api.kamereon import exceptions

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.setup import async_setup_component

from . import (
    create_vehicle_proxy,
    create_vehicle_proxy_with_side_effect,
    setup_renault_integration,
)
from .const import MOCK_VEHICLES

from tests.common import mock_device_registry, mock_registry


@pytest.mark.parametrize("vehicle_type", MOCK_VEHICLES.keys())
async def test_sensors(hass, vehicle_type):
    """Test for Renault sensors."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    vehicle_proxy = await create_vehicle_proxy(hass, vehicle_type)

    with patch(
        "homeassistant.components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("homeassistant.components.renault.PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    mock_vehicle = MOCK_VEHICLES[vehicle_type]
    assert len(device_registry.devices) == 1
    expected_device = mock_vehicle["expected_device"]
    registry_entry = device_registry.async_get_device(expected_device["identifiers"])
    assert registry_entry is not None
    assert registry_entry.identifiers == expected_device["identifiers"]
    assert registry_entry.manufacturer == expected_device["manufacturer"]
    assert registry_entry.name == expected_device["name"]
    assert registry_entry.model == expected_device["model"]
    assert registry_entry.sw_version == expected_device["sw_version"]

    expected_entities = mock_vehicle[SENSOR_DOMAIN]
    assert len(entity_registry.entities) == len(expected_entities)
    for expected_entity in expected_entities:
        entity_id = expected_entity["entity_id"]
        registry_entry = entity_registry.entities.get(entity_id)
        assert registry_entry is not None
        assert registry_entry.unique_id == expected_entity["unique_id"]
        assert registry_entry.unit_of_measurement == expected_entity.get("unit")
        assert registry_entry.device_class == expected_entity.get("class")
        state = hass.states.get(entity_id)
        assert state.state == expected_entity["result"]


@pytest.mark.parametrize("vehicle_type", MOCK_VEHICLES.keys())
async def test_sensor_empty(hass, vehicle_type):
    """Test for Renault sensors with empty data from Renault."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    vehicle_proxy = await create_vehicle_proxy_with_side_effect(hass, vehicle_type, {})

    with patch(
        "homeassistant.components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("homeassistant.components.renault.PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    mock_vehicle = MOCK_VEHICLES[vehicle_type]
    assert len(device_registry.devices) == 1
    expected_device = mock_vehicle["expected_device"]
    registry_entry = device_registry.async_get_device(expected_device["identifiers"])
    assert registry_entry is not None
    assert registry_entry.identifiers == expected_device["identifiers"]
    assert registry_entry.manufacturer == expected_device["manufacturer"]
    assert registry_entry.name == expected_device["name"]
    assert registry_entry.model == expected_device["model"]
    assert registry_entry.sw_version == expected_device["sw_version"]

    expected_entities = mock_vehicle[SENSOR_DOMAIN]
    assert len(entity_registry.entities) == len(expected_entities)
    for expected_entity in expected_entities:
        entity_id = expected_entity["entity_id"]
        registry_entry = entity_registry.entities.get(entity_id)
        assert registry_entry is not None
        assert registry_entry.unique_id == expected_entity["unique_id"]
        assert registry_entry.unit_of_measurement == expected_entity.get("unit")
        assert registry_entry.device_class == expected_entity.get("class")
        state = hass.states.get(entity_id)
        assert state.state == STATE_UNAVAILABLE


@pytest.mark.parametrize("vehicle_type", MOCK_VEHICLES.keys())
async def test_sensor_errors(hass, vehicle_type):
    """Test for Renault sensors with temporary failure."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    invalid_upstream_exception = exceptions.InvalidUpstreamException(
        "err.tech.500",
        "Invalid response from the upstream server (The request sent to the GDC is erroneous) ; 502 Bad Gateway",
    )

    vehicle_proxy = await create_vehicle_proxy_with_side_effect(
        hass, vehicle_type, invalid_upstream_exception
    )

    with patch(
        "homeassistant.components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("homeassistant.components.renault.PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    mock_vehicle = MOCK_VEHICLES[vehicle_type]
    assert len(device_registry.devices) == 1
    expected_device = mock_vehicle["expected_device"]
    registry_entry = device_registry.async_get_device(expected_device["identifiers"])
    assert registry_entry is not None
    assert registry_entry.identifiers == expected_device["identifiers"]
    assert registry_entry.manufacturer == expected_device["manufacturer"]
    assert registry_entry.name == expected_device["name"]
    assert registry_entry.model == expected_device["model"]
    assert registry_entry.sw_version == expected_device["sw_version"]

    expected_entities = mock_vehicle[SENSOR_DOMAIN]
    assert len(entity_registry.entities) == len(expected_entities)
    for expected_entity in expected_entities:
        entity_id = expected_entity["entity_id"]
        registry_entry = entity_registry.entities.get(entity_id)
        assert registry_entry is not None
        assert registry_entry.unique_id == expected_entity["unique_id"]
        assert registry_entry.unit_of_measurement == expected_entity.get("unit")
        assert registry_entry.device_class == expected_entity.get("class")
        state = hass.states.get(entity_id)
        assert state.state == STATE_UNAVAILABLE


async def test_sensor_access_denied(hass):
    """Test for Renault sensors with access denied failure."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    access_denied_exception = exceptions.AccessDeniedException(
        "err.func.403",
        "Access is denied for this resource",
    )

    vehicle_proxy = await create_vehicle_proxy_with_side_effect(
        hass, "zoe_40", access_denied_exception
    )

    with patch(
        "homeassistant.components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("homeassistant.components.renault.PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    assert len(device_registry.devices) == 0
    assert len(entity_registry.entities) == 0


async def test_sensor_not_supported(hass):
    """Test for Renault sensors with access denied failure."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    not_supported_exception = exceptions.NotSupportedException(
        "err.tech.501",
        "This feature is not technically supported by this gateway",
    )

    vehicle_proxy = await create_vehicle_proxy_with_side_effect(
        hass, "zoe_40", not_supported_exception
    )

    with patch(
        "homeassistant.components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("homeassistant.components.renault.PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    assert len(device_registry.devices) == 0
    assert len(entity_registry.entities) == 0
