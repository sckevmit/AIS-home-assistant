"""Set up the demo environment that mimics interaction with devices."""
import asyncio
import json
import logging

from homeassistant.components.ais_dom import ais_global
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.setup import async_setup_component

DOMAIN = "ais_virtual_devices"
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the ais ais environment."""
    # Set up ais dom devices (RF codes)
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            "sensor", "ais_dom_device", {}, config
        )
    )

    # create sensors
    hass.states.async_set("sensor.version_info", "", {"friendly_name": "Wersja"})
    hass.states.async_set("sensor.ais_backup_info", 0, {})
    hass.states.async_set("sensor.ais_db_connection_info", 0, {})
    hass.states.async_set("sensor.ais_logs_settings_info", 0, {})
    hass.states.async_set("sensor.ais_tv_mode", "", {})
    hass.states.async_set("sensor.ais_tv_activity", "", {})
    hass.states.async_set("sensor.ais_spotify_favorites_mode", "", {})
    hass.states.async_set("sensor.ais_radio_origin", "private", {})
    hass.states.async_set("sensor.ais_podcast_origin", "private", {})
    hass.states.async_set(
        "sensor.ais_secure_android_id_dom",
        "",
        {"friendly_name": "Unikalny identyfikator bramki"},
    )
    hass.states.async_set("sensor.ais_gate_model", "", {})
    hass.states.async_set("sensor.selected_entity", "", {})
    hass.states.async_set("sensor.ais_speech_status", "DONE", {})
    hass.states.async_set(
        "binary_sensor.ais_remote_button", "", {"friendly_name": "Kod przycisku"}
    )

    hass.states.async_set(
        "sensor.internal_ip_address",
        "",
        {"friendly_name": "Lokalny adres IP", "icon": "mdi:access-point-network"},
    )

    hass.states.async_set(
        "sensor.local_host_name",
        "",
        {"friendly_name": "Lokalna nazwa hosta", "icon": "mdi:dns"},
    )

    hass.states.async_set(
        "sensor.gate_pairing_pin",
        "",
        {"friendly_name": "Kod PIN", "icon": "mdi:textbox-password"},
    )

    # create groups for remote

    #
    # # # Mój Dom
    #
    hass.states.async_set(
        "group.all_ais_persons",
        "on",
        {
            "entity_id": [],
            "order": 1,
            "control": "hidden",
            "friendly_name": "Osoby",
            "context_key_words": "osoby",
            "context_answer": "OK, osoby",
            "remote_group_view": "Mój Dom",
        },
    )

    hass.states.async_set(
        "group.all_ais_switches",
        "",
        {
            "entity_id": [],
            "order": 1,
            "control": "hidden",
            "friendly_name": "Przełączniki",
            "context_key_words": "przełaczniki",
            "context_answer": "OK, wybrano wszystkie przełączniki. Możesz powiedzieć co włączyć lub nawigować pilotem "
                              "by sprawdzać status oraz przełączać.",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_lights",
        "",
        {
            "entity_id": [],
            "order": 2,
            "control": "hidden",
            "friendly_name": "Światła",
            "context_key_words": "światła",
            "context_answer": "OK, wybrano wszystkie światła. Możesz powiedzieć co włączyć lub nawigować pilotem by "
                              "sprawdzać status oraz przełączać",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_sensors",
        "",
        {
            "entity_id": [],
            "order": 3,
            "control": "hidden",
            "friendly_name": "Czujniki",
            "context_key_words": "czujniki",
            "context_answer": "OK, wybrano wszystkie czujniki.",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_climates",
        "",
        {
            "entity_id": [],
            "order": 4,
            "control": "hidden",
            "friendly_name": "Termostaty",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_covers",
        "",
        {
            "entity_id": [],
            "order": 5,
            "control": "hidden",
            "friendly_name": "Zasłony",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_vacuums",
        "",
        {
            "entity_id": [],
            "order": 6,
            "control": "hidden",
            "friendly_name": "Odkurzacze",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_locks",
        "",
        {
            "entity_id": [],
            "order": 7,
            "control": "hidden",
            "friendly_name": "Zamki",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_cameras",
        "",
        {
            "entity_id": [],
            "order": 8,
            "control": "hidden",
            "friendly_name": "Kamery",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_fans",
        "",
        {
            "entity_id": [],
            "order": 9,
            "control": "hidden",
            "friendly_name": "Wentylatory",
            "remote_group_view": "group.all_ais_devices",
        },
    )

    hass.states.async_set(
        "group.all_ais_devices",
        "",
        {
            "entity_id": [
                "group.all_ais_switches",
                "group.all_ais_lights",
                "group.all_ais_sensors",
                "group.all_ais_climates",
                "group.all_ais_covers",
                "group.all_ais_vacuums",
                "group.all_ais_locks",
                "group.all_ais_cameras",
                "group.all_ais_fans",
            ],
            "order": 2,
            "control": "hidden",
            "friendly_name": "Urządzenia",
            "context_key_words": "urządzenia",
            "context_answer": "OK, wybrano wszystkie urządzenia. Możesz powiedzieć co włączyć lub nawigować pilotem "
                              "by sprawdzać status oraz przełączać.",
            "remote_group_view": "Mój Dom",
        },
    )

    hass.states.async_set(
        "group.all_ais_automations",
        "on",
        {
            "entity_id": [],
            "order": 3,
            "control": "hidden",
            "friendly_name": "Automatyzacje",
            "remote_group_view": "Mój Dom",
        },
    )

    hass.states.async_set(
        "group.all_ais_scenes",
        "on",
        {
            "entity_id": [],
            "order": 4,
            "control": "hidden",
            "friendly_name": "Sceny",
            "remote_group_view": "Mój Dom",
        },
    )

    hass.states.async_set(
        "group.day_info",
        "on",
        {
            "entity_id": ["binary_sensor.dzien_pracujacy"],
            "order": 6,
            "control": "hidden",
            "friendly_name": "Kalendarium",
            "remote_group_view": "Mój Dom",
        },
    )

    #
    # # # Audio
    #
    hass.states.async_set(
        "group.ais_favorites",
        "on",
        {
            "entity_id": ["sensor.aisfavoriteslist"],
            "order": 1,
            "control": "hidden",
            "friendly_name": "Wszystkie ulubione",
            "context_key_words": "ulubione",
            "context_answer": "OK, wybierz pozycję",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.ais_bookmarks",
        "on",
        {
            "entity_id": ["sensor.aisbookmarkslist"],
            "order": 2,
            "control": "hidden",
            "friendly_name": "Wszystkie zakładki",
            "context_key_words": "zakładki",
            "context_answer": "OK, wybierz pozycję",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.ais_rss_news_remote",
        "on",
        {
            "entity_id": [
                "input_select.rss_news_category",
                "input_select.rss_news_channel",
                "sensor.rssnewslist",
            ],
            "order": 3,
            "control": "hidden",
            "friendly_name": "Wiadomości",
            "context_key_words": "wiadomości,informacje",
            "context_answer": "OK, wybierz pilotem kategorię, kanał i artykuł który mam przeczytać",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.local_audio",
        "on",
        {
            "entity_id": ["sensor.ais_drives"],
            "order": 4,
            "control": "hidden",
            "friendly_name": "Dyski",
            "context_key_words": "lokalne pliki,dyski",
            "context_answer": "OK, wybierz plik",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.radio_player",
        "on",
        {
            "entity_id": ["input_select.radio_type", "sensor.radiolist"],
            "order": 5,
            "control": "hidden",
            "friendly_name": "Radia Internetowe",
            "context_suffix": "Radio",
            "context_key_words": "radio,radia,radia internetowe",
            "context_answer": "OK, powiedz jakiej stacji chcesz posłuchać lub wybierz pilotem typ radia i stację "
                              "radiową",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.podcast_player",
        "on",
        {
            "entity_id": [
                "input_select.podcast_type",
                "sensor.podcastnamelist",
                "sensor.podcastlist",
            ],
            "order": 6,
            "control": "hidden",
            "friendly_name": "Podcasty",
            "context_suffix": "Podcast",
            "context_key_words": "podcast,podcasty,podkasty,podkast",
            "context_answer": "OK, powiedz jaką audycję mam włączyć lub wybierz pilotem typ, "
                              "audycję i odcinek podcasta",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.audiobooks_player",
        "on",
        {
            "entity_id": [
                "input_select.book_autor",
                "sensor.audiobookslist",
                "sensor.audiobookschapterslist",
            ],
            "order": 7,
            "control": "hidden",
            "friendly_name": "Audio Książki Online",
            "context_suffix": "Książka",
            "context_key_words": "książki,książka,audiobook,audiobooks",
            "context_answer": "OK, powiedz jakiej książki chcesz posłuchać lub wybierz pilotem autora, książkę i "
                              "rozdział książki",
            "remote_group_view": "Audio",
        },
    )

    hass.states.async_set(
        "group.music_player",
        "on",
        {
            "entity_id": [
                "input_select.ais_music_service",
                "input_text.ais_music_query",
                "input_text.ais_spotify_query",
                "sensor.youtubelist",
                "sensor.spotifysearchlist",
                "sensor.spotifylist",
            ],
            "order": 8,
            "control": "hidden",
            "friendly_name": "Muzyka",
            "context_suffix": "Muzyka",
            "context_key_words": "youtube,muzyka,yt,tuba,spotify",
            "context_answer": "OK, powiedz jakiej muzyki chcesz posłuchać",
            "remote_group_view": "Audio",
        },
    )

    #
    # # # Ustawienia
    #

    hass.states.async_set(
        "group.internet_status",
        "on",
        {
            "entity_id": [
                "sensor.local_host_name",
                "sensor.internal_ip_address",
                "sensor.ais_wifi_service_current_network_info",
                "script.ais_scan_android_wifi_network",
                "input_select.ais_android_wifi_network",
                "input_text.ais_android_wifi_password",
                "script.ais_connect_android_wifi_network",
            ],
            "order": 1,
            "control": "hidden",
            "friendly_name": "Ustawienia sieci",
            "context_key_words": "internet,sieć,ustawienia sieci,wifi",
            "context_answer": "OK, wybrano internet. Możesz nawigowac pilotem by uzyskać informację o statusie Twojej "
                              "sieci.",
            "remote_group_view": "Ustawienia",
        },
    )

    hass.states.async_set(
        "group.ais_add_iot_device",
        "on",
        {
            "entity_id": [
                "sensor.ais_connect_iot_device_info",
                "script.ais_scan_iot_devices_in_network",
                "input_select.ais_iot_devices_in_network",
                "input_select.ais_android_wifi_network",
                "input_text.ais_iot_device_wifi_password",
                "input_text.ais_iot_device_name",
                "script.ais_connect_iot_device_to_network",
            ],
            "order": 2,
            "control": "hidden",
            "friendly_name": "Dodaj nowe urządzenia",
            "context_key_words": "dodaj urządzenie",
            "context_answer": "OK, wybrano dodawanie nowego urządzenia. Możesz nawigowac pilotem by dodać urządzenie "
                              "do systemu.",
            "remote_group_view": "Ustawienia",
        },
    )

    hass.states.async_set(
        "group.audio_player",
        "on",
        {
            "entity_id": [
                "media_player.wbudowany_glosnik",
                "input_select.media_player_sound_mode",
                "input_number.media_player_speed",
                "input_boolean.ais_audio_mono",
            ],
            "order": 3,
            "control": "hidden",
            "friendly_name": "Odtwarzacze",
            "context_key_words": "odtwarzacz, odtwarzacze",
            "context_answer": "OK, wybrano odtwarzacze.",
            "remote_group_view": "Ustawienia",
        },
    )

    hass.states.async_set(
        "group.ais_tts_configuration",
        "on",
        {
            "entity_id": [
                "input_select.assistant_voice",
                "input_number.assistant_rate",
                "input_number.assistant_tone",
                "input_boolean.ais_quiet_mode",
                "input_datetime.ais_quiet_mode_start",
                "input_datetime.ais_quiet_mode_stop",
            ],
            "order": 4,
            "control": "hidden",
            "friendly_name": "Wybór głosu Asystenta",
            "context_key_words": "głos,ustawienia głosu",
            "context_answer": "OK, wybrano konfigurację zamiany tekstu na mowę.",
            "remote_group_view": "Ustawienia",
        },
    )

    #
    # # # System i Pomoc
    #
    hass.states.async_set(
        "group.dom_system_version",
        "on",
        {
            "entity_id": [
                "sensor.version_info",
                "script.ais_update_system",
                "input_boolean.ais_auto_update",
                "input_boolean.ais_remote_access",
                "sensor.ais_secure_android_id_dom",
                "script.ais_cloud_sync",
                "script.ais_restart_system",
                "script.ais_stop_system",
            ],
            "order": 1,
            "control": "hidden",
            "friendly_name": "System",
            "context_key_words": "wersja,aktualizacja,wersja systemu",
            "context_answer": "OK, wybrano informację o wersji. Możesz nawigować pilotem by sprawdzić dostępność "
                              "aktualizacji systemu",
            "remote_group_view": "Pomoc",
        },
    )

    hass.states.async_set(
        "group.ais_rss_help_remote",
        "on",
        {
            "entity_id": ["input_select.ais_rss_help_topic"],
            "order": 2,
            "control": "hidden",
            "friendly_name": "Instrukcja",
            "context_key_words": "instrukcja,pomoc,pomocy,help",
            "context_answer": "OK, wybierz pilotem stronę pomocy",
            "remote_group_view": "Pomoc",
        },
    )

    # LOG settings
    try:
        with open(
                hass.config.config_dir + ais_global.G_LOG_SETTINGS_INFO_FILE
        ) as json_file:
            log_settings = json.load(json_file)
        ais_global.G_LOG_SETTINGS_INFO = log_settings
    except Exception as e:
        _LOGGER.info("Error get log settings info " + str(e))

    if ais_global.G_LOG_SETTINGS_INFO is not None:
        # set the logs settings info
        hass.states.async_set(
            "sensor.ais_logs_settings_info", "1", ais_global.G_LOG_SETTINGS_INFO
        )
        # re-set log level
        hass.async_add_job(
            hass.services.async_call(
                "logger",
                "set_default_level",
                {"level": ais_global.G_LOG_SETTINGS_INFO["logLevel"]},
            )
        )

    # DB settings
    try:
        with open(
                hass.config.config_dir + ais_global.G_DB_SETTINGS_INFO_FILE
        ) as json_file:
            db_settings = json.load(json_file)
        ais_global.G_DB_SETTINGS_INFO = db_settings
        if "dbKeepDays" not in ais_global.G_DB_SETTINGS_INFO:
            ais_global.G_DB_SETTINGS_INFO["dbKeepDays"] = 10
        if "dbShowHistory" not in ais_global.G_DB_SETTINGS_INFO:
            ais_global.G_DB_SETTINGS_INFO["dbShowHistory"] = False
        if "dbShowLogbook" not in ais_global.G_DB_SETTINGS_INFO:
            ais_global.G_DB_SETTINGS_INFO["dbShowLogbook"] = False
        if "dbInclude" not in ais_global.G_DB_SETTINGS_INFO:
            ais_global.G_DB_SETTINGS_INFO["dbInclude"] = ais_global.G_AIS_INCLUDE_DB_DEFAULT
        if "dbExclude" not in ais_global.G_DB_SETTINGS_INFO:
            ais_global.G_DB_SETTINGS_INFO["dbExclude"] = ais_global.G_AIS_EXCLUDE_DB_DEFAULT_EMPTY
    except Exception as e:
        _LOGGER.info("Error get db settings info " + str(e))
        ais_global.G_DB_SETTINGS_INFO = {"dbInclude": ais_global.G_AIS_INCLUDE_DB_DEFAULT,
                                         "dbExclude": ais_global.G_AIS_EXCLUDE_DB_DEFAULT_EMPTY}

    if ais_global.G_DB_SETTINGS_INFO is not None:
        # set the logs settings info
        hass.states.async_set(
            "sensor.ais_db_connection_info", "0", ais_global.G_DB_SETTINGS_INFO
        )

        if (
                not hass.services.has_service("recorder", "purge")
                and "dbEngine" in ais_global.G_DB_SETTINGS_INFO
                and len(ais_global.G_DB_SETTINGS_INFO["dbEngine"]) > 1
        ):
            hass.async_create_task(
                hass.helpers.discovery.async_load_platform(
                    "recorder", "recorder", {}, config
                )
            )

        if "dbShowLogbook" in ais_global.G_DB_SETTINGS_INFO:
            # logbook
            if "logbook" not in hass.data.get(hass.components.frontend.DATA_PANELS, {}):
                hass.async_create_task(
                    hass.helpers.discovery.async_load_platform(
                        "logbook", "logbook", {}, config
                    )
                )

        if "dbShowHistory" in ais_global.G_DB_SETTINGS_INFO:
            # history
            if "history" not in hass.data.get(hass.components.frontend.DATA_PANELS, {}):
                hass.async_create_task(
                    hass.helpers.discovery.async_load_platform(
                        "history", "history", {}, config
                    )
                )

    return True
