"""Recycling platform"""
import asyncio
import logging
from datetime import timedelta, datetime, date
from typing import Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_NAME,
    ATTR_ATTRIBUTION,
)

import myfitnesspal as ext_myfitnesspal

from .const import DOMAIN, STARTUP_MESSAGE, PLATFORMS, ATTRIBUTION


SCAN_INTERVAL = timedelta(minutes=5)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured MFP."""
    # We allow setup only through config flow type of config
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up MFP as config entry."""

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = config_entry.data.get(CONF_USERNAME)
    password = config_entry.data.get(CONF_PASSWORD)
    display_name = config_entry.data.get(CONF_NAME)

    # Lib does I/O in the init...
    def wrap_client():
        """Wrap the fitnesspal client."""
        return ext_myfitnesspal.Client(username, password)

    client = await hass.async_add_executor_job(wrap_client)

    coordinator = MyFitnessPalDataUpdateCoordinator(
        hass, client=client, display_name=display_name
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if config_entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(config_entry, platform)
            )

    config_entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class MyFitnessPalDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: ext_myfitnesspal.Client, display_name: str
    ):
        """Initialize."""

        self.client = client
        self.display_name = display_name
        self.unit_of_weight = "kg" if hass.config.units.is_metric else "lb"

        if len(self.display_name) == 0:
            self.display_name = self._username

        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            data = await self.hass.async_add_executor_job(self.update_data_sync)
            return data
        except Exception as exception:
            raise UpdateFailed(exception)

    def update_data_sync(self) -> Dict[str, str]:
        """Get the actual data from the API"""

        today = date.today()
        latest_weight = 0

        info = self.client.get_date(today.year, today.month, today.day)
        weights = self.client.get_measurements("Weight")
        if len(weights) > 0:
            latest_record = weights.popitem(last=False)
            if len(latest_record) > 1:
                latest_weight = latest_record[1]

        goal_calories = info.goals.get("calories",
            round(info.goals.get("kilojoules", 0)  / 4.184)
        )
        goal_kilojoules = info.goals.get("kilojoules",
            round(info.goals.get("calories", 0) * 4.184)
        )
        goal_carbohydrates = info.goals.get("carbohydrates", 0)
        goal_fat = info.goals.get("fat", 0)
        goal_sodium = info.goals.get("sodium", 0)
        goal_sugar = info.goals.get("sugar", 0)
        goal_protein = info.goals.get("protein", 0)

        total_calories = info.totals.get("calories",
            round(info.totals.get("kilojoules", 0)  / 4.184)
        )
        total_kilojoules = info.totals.get("kilojoules",
            round(info.totals.get("calories", 0) * 4.184)
        )
        total_carbohydrates = info.totals.get("carbohydrates", 0)
        total_fat = info.totals.get("fat", 0)
        total_sodium = info.totals.get("sodium", 0)
        total_sugar = info.totals.get("sugar", 0)
        total_protein = info.totals.get("protein", 0)
        water = info.water
        _, weight = list(weights.items())[0] if len(weights) > 0 else 0, 0

        cardio_calories_burned = 0
        cardio_kilojoules_burned = 0
        for exercise in info.exercises[0]:
            cardio_calories_burned += exercise.totals.get("calories burned",
                round(exercise.totals.get("kilojoules burned", 0)  / 4.184)
            )
            cardio_kilojoules_burned += exercise.totals.get("kilojoules burned",
                round(exercise.totals.get("calories burned", 0) * 4.184)
            )

        result = {}            
            
        for meal in info.meals:
            meal_name = mail._name.replace(" ", "")
            result["meal_" + meal_name + "_calories"] = meal.totals.get("calories")
            result["meal_" + meal_name + "_carbohydrates"] = meal.totals.get("carbohydrates")
            result["meal_" + meal_name + "_protein"] = meal.totals.get("protein")            
            result["meal_" + meal_name + "_fat"] = meal.totals.get("fat")
            result["meal_" + meal_name + "_sodium"] = meal.totals.get("sodium")            
            result["meal_" + meal_name + "_sugar"] = meal.totals.get("sugar")

        result["goal_calories"] = goal_calories
        result["goal_kilojoules"] = goal_kilojoules
        result["goal_carbohydrates"] = goal_carbohydrates
        result["goal_fat"] = goal_fat
        result["goal_sodium"] = goal_sodium
        result["goal_sugar"] = goal_sugar
        result["goal_protein"] = goal_protein

        result["total_calories"] = total_calories
        result["total_kilojoules"] = total_kilojoules
        result["total_carbohydrates"] = total_carbohydrates
        result["total_fat"] = total_fat
        result["total_sodium"] = total_sodium
        result["total_sugar"] = total_sugar
        result["total_protein"] = total_protein

        result["cardio_kilojoules_burned"] = cardio_kilojoules_burned
        result["cardio_calories_burned"] = cardio_calories_burned
        result["water"] = water
        result["weight"] = latest_weight
        result["cal_remaining"] = goal_calories - total_calories
        result["kj_remaining"] = goal_kilojoules - total_kilojoules
        result["cal_remaining_ex_workout"] = (
            goal_calories - total_calories - cardio_calories_burned
        )
        result["kj_remaining_ex_workout"] = (
            goal_kilojoules - total_kilojoules - cardio_kilojoules_burned
        )
        result["cal_goal"] = goal_calories - cardio_calories_burned
        result["kj_goal"] = goal_kilojoules - cardio_kilojoules_burned
        result["goal_pct"] = round(
            (total_kilojoules / (goal_kilojoules + cardio_kilojoules_burned)) * 100,
            0,
        )

        result[ATTR_ATTRIBUTION] = ATTRIBUTION

        return result
