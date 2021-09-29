"""The tests for sensor recorder platform."""
# pylint: disable=protected-access,invalid-name
from datetime import timedelta
from unittest.mock import patch, sentinel

import pytest
from pytest import approx

from homeassistant.components.recorder import history
from homeassistant.components.recorder.const import DATA_INSTANCE
from homeassistant.components.recorder.models import (
    Statistics,
    process_timestamp_to_utc_isoformat,
)
from homeassistant.components.recorder.statistics import (
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.setup import setup_component
import homeassistant.util.dt as dt_util

from tests.common import mock_registry
from tests.components.recorder.common import wait_recording_done


def test_compile_hourly_statistics(hass_recorder):
    """Test compiling hourly statistics."""
    hass = hass_recorder()
    recorder = hass.data[DATA_INSTANCE]
    setup_component(hass, "sensor", {})
    zero, four, states = record_states(hass)
    hist = history.get_significant_states(hass, zero, four)
    assert dict(states) == dict(hist)

    for kwargs in ({}, {"statistic_ids": ["sensor.test1"]}):
        stats = statistics_during_period(hass, zero, **kwargs)
        assert stats == {}
    stats = get_last_statistics(hass, 0, "sensor.test1", True)
    assert stats == {}

    recorder.do_adhoc_statistics(period="hourly", start=zero)
    recorder.do_adhoc_statistics(period="hourly", start=four)
    wait_recording_done(hass)
    expected_1 = {
        "statistic_id": "sensor.test1",
        "start": process_timestamp_to_utc_isoformat(zero),
        "mean": approx(14.915254237288135),
        "min": approx(10.0),
        "max": approx(20.0),
        "last_reset": None,
        "state": None,
        "sum": None,
    }
    expected_2 = {
        "statistic_id": "sensor.test1",
        "start": process_timestamp_to_utc_isoformat(four),
        "mean": approx(20.0),
        "min": approx(20.0),
        "max": approx(20.0),
        "last_reset": None,
        "state": None,
        "sum": None,
    }
    expected_stats1 = [
        {**expected_1, "statistic_id": "sensor.test1"},
        {**expected_2, "statistic_id": "sensor.test1"},
    ]
    expected_stats2 = [
        {**expected_1, "statistic_id": "sensor.test2"},
        {**expected_2, "statistic_id": "sensor.test2"},
    ]

    # Test statistics_during_period
    stats = statistics_during_period(hass, zero)
    assert stats == {"sensor.test1": expected_stats1, "sensor.test2": expected_stats2}

    stats = statistics_during_period(hass, zero, statistic_ids=["sensor.test2"])
    assert stats == {"sensor.test2": expected_stats2}

    stats = statistics_during_period(hass, zero, statistic_ids=["sensor.test3"])
    assert stats == {}

    # Test get_last_statistics
    stats = get_last_statistics(hass, 0, "sensor.test1", True)
    assert stats == {}

    stats = get_last_statistics(hass, 1, "sensor.test1", True)
    assert stats == {"sensor.test1": [{**expected_2, "statistic_id": "sensor.test1"}]}

    stats = get_last_statistics(hass, 2, "sensor.test1", True)
    assert stats == {"sensor.test1": expected_stats1[::-1]}

    stats = get_last_statistics(hass, 3, "sensor.test1", True)
    assert stats == {"sensor.test1": expected_stats1[::-1]}

    stats = get_last_statistics(hass, 1, "sensor.test3", True)
    assert stats == {}


@pytest.fixture
def mock_sensor_statistics():
    """Generate some fake statistics."""
    sensor_stats = {
        "meta": {"unit_of_measurement": "dogs", "has_mean": True, "has_sum": False},
        "stat": {},
    }

    def get_fake_stats():
        return {
            "sensor.test1": sensor_stats,
            "sensor.test2": sensor_stats,
            "sensor.test3": sensor_stats,
        }

    with patch(
        "homeassistant.components.sensor.recorder.compile_statistics",
        return_value=get_fake_stats(),
    ):
        yield


@pytest.fixture
def mock_from_stats():
    """Mock out Statistics.from_stats."""
    counter = 0
    real_from_stats = Statistics.from_stats

    def from_stats(metadata_id, start, stats):
        nonlocal counter
        if counter == 0 and metadata_id == 2:
            counter += 1
            return None
        return real_from_stats(metadata_id, start, stats)

    with patch(
        "homeassistant.components.recorder.statistics.Statistics.from_stats",
        side_effect=from_stats,
        autospec=True,
    ):
        yield


def test_compile_hourly_statistics_exception(
    hass_recorder, mock_sensor_statistics, mock_from_stats
):
    """Test exception handling when compiling hourly statistics."""

    def mock_from_stats():
        raise ValueError

    hass = hass_recorder()
    recorder = hass.data[DATA_INSTANCE]
    setup_component(hass, "sensor", {})

    now = dt_util.utcnow()
    recorder.do_adhoc_statistics(period="hourly", start=now)
    recorder.do_adhoc_statistics(period="hourly", start=now + timedelta(hours=1))
    wait_recording_done(hass)
    expected_1 = {
        "statistic_id": "sensor.test1",
        "start": process_timestamp_to_utc_isoformat(now),
        "mean": None,
        "min": None,
        "max": None,
        "last_reset": None,
        "state": None,
        "sum": None,
    }
    expected_2 = {
        "statistic_id": "sensor.test1",
        "start": process_timestamp_to_utc_isoformat(now + timedelta(hours=1)),
        "mean": None,
        "min": None,
        "max": None,
        "last_reset": None,
        "state": None,
        "sum": None,
    }
    expected_stats1 = [
        {**expected_1, "statistic_id": "sensor.test1"},
        {**expected_2, "statistic_id": "sensor.test1"},
    ]
    expected_stats2 = [
        {**expected_2, "statistic_id": "sensor.test2"},
    ]
    expected_stats3 = [
        {**expected_1, "statistic_id": "sensor.test3"},
        {**expected_2, "statistic_id": "sensor.test3"},
    ]

    stats = statistics_during_period(hass, now)
    assert stats == {
        "sensor.test1": expected_stats1,
        "sensor.test2": expected_stats2,
        "sensor.test3": expected_stats3,
    }


def test_rename_entity(hass_recorder):
    """Test statistics is migrated when entity_id is changed."""
    hass = hass_recorder()
    recorder = hass.data[DATA_INSTANCE]
    setup_component(hass, "sensor", {})

    entity_reg = mock_registry(hass)
    reg_entry = entity_reg.async_get_or_create(
        "sensor",
        "test",
        "unique_0000",
        suggested_object_id="test1",
    )
    assert reg_entry.entity_id == "sensor.test1"

    zero, four, states = record_states(hass)
    hist = history.get_significant_states(hass, zero, four)
    assert dict(states) == dict(hist)

    for kwargs in ({}, {"statistic_ids": ["sensor.test1"]}):
        stats = statistics_during_period(hass, zero, **kwargs)
        assert stats == {}
    stats = get_last_statistics(hass, 0, "sensor.test1", True)
    assert stats == {}

    recorder.do_adhoc_statistics(period="hourly", start=zero)
    wait_recording_done(hass)
    expected_1 = {
        "statistic_id": "sensor.test1",
        "start": process_timestamp_to_utc_isoformat(zero),
        "mean": approx(14.915254237288135),
        "min": approx(10.0),
        "max": approx(20.0),
        "last_reset": None,
        "state": None,
        "sum": None,
    }
    expected_stats1 = [
        {**expected_1, "statistic_id": "sensor.test1"},
    ]
    expected_stats2 = [
        {**expected_1, "statistic_id": "sensor.test2"},
    ]
    expected_stats99 = [
        {**expected_1, "statistic_id": "sensor.test99"},
    ]

    stats = statistics_during_period(hass, zero)
    assert stats == {"sensor.test1": expected_stats1, "sensor.test2": expected_stats2}

    entity_reg.async_update_entity(reg_entry.entity_id, new_entity_id="sensor.test99")
    hass.block_till_done()

    stats = statistics_during_period(hass, zero)
    assert stats == {"sensor.test99": expected_stats99, "sensor.test2": expected_stats2}


def test_statistics_duplicated(hass_recorder, caplog):
    """Test statistics with same start time is not compiled."""
    hass = hass_recorder()
    recorder = hass.data[DATA_INSTANCE]
    setup_component(hass, "sensor", {})
    zero, four, states = record_states(hass)
    hist = history.get_significant_states(hass, zero, four)
    assert dict(states) == dict(hist)

    wait_recording_done(hass)
    assert "Compiling statistics for" not in caplog.text
    assert "Statistics already compiled" not in caplog.text

    with patch(
        "homeassistant.components.sensor.recorder.compile_statistics"
    ) as compile_statistics:
        recorder.do_adhoc_statistics(period="hourly", start=zero)
        wait_recording_done(hass)
        assert compile_statistics.called
        compile_statistics.reset_mock()
        assert "Compiling statistics for" in caplog.text
        assert "Statistics already compiled" not in caplog.text
        caplog.clear()

        recorder.do_adhoc_statistics(period="hourly", start=zero)
        wait_recording_done(hass)
        assert not compile_statistics.called
        compile_statistics.reset_mock()
        assert "Compiling statistics for" not in caplog.text
        assert "Statistics already compiled" in caplog.text
        caplog.clear()


def record_states(hass):
    """Record some test states.

    We inject a bunch of state updates temperature sensors.
    """
    mp = "media_player.test"
    sns1 = "sensor.test1"
    sns2 = "sensor.test2"
    sns3 = "sensor.test3"
    sns4 = "sensor.test4"
    sns1_attr = {
        "device_class": "temperature",
        "state_class": "measurement",
        "unit_of_measurement": TEMP_CELSIUS,
    }
    sns2_attr = {
        "device_class": "humidity",
        "state_class": "measurement",
        "unit_of_measurement": "%",
    }
    sns3_attr = {"device_class": "temperature"}
    sns4_attr = {}

    def set_state(entity_id, state, **kwargs):
        """Set the state."""
        hass.states.set(entity_id, state, **kwargs)
        wait_recording_done(hass)
        return hass.states.get(entity_id)

    zero = dt_util.utcnow()
    one = zero + timedelta(minutes=1)
    two = one + timedelta(minutes=15)
    three = two + timedelta(minutes=30)
    four = three + timedelta(minutes=15)

    states = {mp: [], sns1: [], sns2: [], sns3: [], sns4: []}
    with patch("homeassistant.components.recorder.dt_util.utcnow", return_value=one):
        states[mp].append(
            set_state(mp, "idle", attributes={"media_title": str(sentinel.mt1)})
        )
        states[mp].append(
            set_state(mp, "YouTube", attributes={"media_title": str(sentinel.mt2)})
        )
        states[sns1].append(set_state(sns1, "10", attributes=sns1_attr))
        states[sns2].append(set_state(sns2, "10", attributes=sns2_attr))
        states[sns3].append(set_state(sns3, "10", attributes=sns3_attr))
        states[sns4].append(set_state(sns4, "10", attributes=sns4_attr))

    with patch("homeassistant.components.recorder.dt_util.utcnow", return_value=two):
        states[sns1].append(set_state(sns1, "15", attributes=sns1_attr))
        states[sns2].append(set_state(sns2, "15", attributes=sns2_attr))
        states[sns3].append(set_state(sns3, "15", attributes=sns3_attr))
        states[sns4].append(set_state(sns4, "15", attributes=sns4_attr))

    with patch("homeassistant.components.recorder.dt_util.utcnow", return_value=three):
        states[sns1].append(set_state(sns1, "20", attributes=sns1_attr))
        states[sns2].append(set_state(sns2, "20", attributes=sns2_attr))
        states[sns3].append(set_state(sns3, "20", attributes=sns3_attr))
        states[sns4].append(set_state(sns4, "20", attributes=sns4_attr))

    return zero, four, states
