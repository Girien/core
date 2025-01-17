"""Support for SleepIQ buttons."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from asyncsleepiq import SleepIQBed

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SleepIQDataUpdateCoordinator
from .entity import SleepIQEntity


@dataclass
class SleepIQButtonEntityDescriptionMixin:
    """Describes a SleepIQ Button entity."""

    press_action: Callable[[SleepIQBed], Any]


@dataclass
class SleepIQButtonEntityDescription(
    ButtonEntityDescription, SleepIQButtonEntityDescriptionMixin
):
    """Class to describe a Button entity."""


ENTITY_DESCRIPTIONS = [
    SleepIQButtonEntityDescription(
        key="calibrate",
        name="Calibrate",
        press_action=lambda client: client.calibrate(),
        icon="mdi:target",
    ),
    SleepIQButtonEntityDescription(
        key="stop-pump",
        name="Stop Pump",
        press_action=lambda client: client.stop_pump(),
        icon="mdi:stop",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sleep number buttons."""
    coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SleepNumberButton(bed, ed)
        for bed in coordinator.client.beds.values()
        for ed in ENTITY_DESCRIPTIONS
    )


class SleepNumberButton(SleepIQEntity, ButtonEntity):
    """Representation of an SleepIQ button."""

    entity_description: SleepIQButtonEntityDescription

    def __init__(
        self, bed: SleepIQBed, entity_description: SleepIQButtonEntityDescription
    ) -> None:
        """Initialize the Button."""
        super().__init__(bed)
        self._attr_name = f"SleepNumber {bed.name} {entity_description.name}"
        self._attr_unique_id = f"{bed.id}-{entity_description.key}"
        self.entity_description = entity_description

    async def async_press(self) -> None:
        """Press the button."""
        await self.entity_description.press_action(self.bed)
