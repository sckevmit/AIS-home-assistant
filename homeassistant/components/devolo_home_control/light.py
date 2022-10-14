"""Platform for light integration."""
from __future__ import annotations

from typing import Any

from devolo_home_control_api.devices.zwave import Zwave
from devolo_home_control_api.homecontrol import HomeControl

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .devolo_multi_level_switch import DevoloMultiLevelSwitchDeviceEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Get all light devices and setup them via config entry."""
    entities = []

    for gateway in hass.data[DOMAIN][entry.entry_id]["gateways"]:
        for device in gateway.multi_level_switch_devices:
            for multi_level_switch in device.multi_level_switch_property.values():
                if multi_level_switch.switch_type == "dimmer":
                    entities.append(
                        DevoloLightDeviceEntity(
                            homecontrol=gateway,
                            device_instance=device,
                            element_uid=multi_level_switch.element_uid,
                        )
                    )

    async_add_entities(entities, False)


class DevoloLightDeviceEntity(DevoloMultiLevelSwitchDeviceEntity, LightEntity):
    """Representation of a light within devolo Home Control."""

    def __init__(
        self, homecontrol: HomeControl, device_instance: Zwave, element_uid: str
    ) -> None:
        """Initialize a devolo multi level switch."""
        super().__init__(
            homecontrol=homecontrol,
            device_instance=device_instance,
            element_uid=element_uid,
        )

        self._attr_supported_features = SUPPORT_BRIGHTNESS
        self._binary_switch_property = device_instance.binary_switch_property.get(
            element_uid.replace("Dimmer", "BinarySwitch")
        )

    @property
    def brightness(self) -> int:
        """Return the brightness value of the light."""
        return round(self._value / 100 * 255)

    @property
    def is_on(self) -> bool:
        """Return the state of the light."""
        return bool(self._value)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn device on."""
        if kwargs.get(ATTR_BRIGHTNESS) is not None:
            self._multi_level_switch_property.set(
                round(kwargs[ATTR_BRIGHTNESS] / 255 * 100)
            )
        else:
            if self._binary_switch_property is not None:
                # Turn on the light device to the latest known value. The value is known by the device itself.
                self._binary_switch_property.set(True)
            else:
                # If there is no binary switch attached to the device, turn it on to 100 %.
                self._multi_level_switch_property.set(100)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        if self._binary_switch_property is not None:
            self._binary_switch_property.set(False)
        else:
            self._multi_level_switch_property.set(0)