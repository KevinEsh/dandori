import pytest
from datetime import datetime, timedelta
from scheduler.helpers.datetools import to_int, to_iso8601, is_intersected
from scheduler.models import Demand
from tests.fixtures import random_datetime


@pytest.mark.parametrize("seconds", [1.5, 2.0, 1000])
def test_to_int_seconds(seconds):
    a = datetime.now()
    dt = timedelta(seconds=seconds)
    b = a + dt
    assert to_int(b, pivot=a, scale="seconds") == round(seconds), \
        "Funcion de to_int no esta regresando el valor correcto"


@pytest.mark.parametrize("minutes", [1.5, 2.0, 1000])
def test_to_int_minutes(minutes):
    a = datetime.now()
    dt = timedelta(minutes=minutes)
    b = a + dt
    assert to_int(b, pivot=a, scale="minutes") == round(minutes), \
        "Funcion de to_int no esta regresando el valor correcto"


@pytest.mark.parametrize("hours", [1.5, 2.0, 1000])
def test_to_int_hours(hours):
    a = datetime.now()
    dt = timedelta(hours=hours)
    b = a + dt
    assert to_int(b, pivot=a, scale="hours") == round(hours), \
        "Funcion de to_int no esta regresando el valor correcto"


@pytest.mark.parametrize("days", [1.5, 2.0, 1000])
def test_to_int_days(days):
    a = datetime.now()
    dt = timedelta(days=days)
    b = a + dt
    assert to_int(b, pivot=a, scale="days") == round(days), \
        "Funcion de to_int no esta regresando el valor correcto"


@pytest.mark.parametrize("scale", ["calabaza", "Seconds", "ora", "ano"])
def test_to_int_scale_exception(scale):
    a = datetime.now()
    dt = timedelta(seconds=100)
    b = a + dt
    with pytest.raises(RuntimeError, match=r"Scale '[A-za-z]*' not registered. You may try one of the followings: \d*"):
        to_int(a, b, scale)


def test_to_iso8601_TZ(random_datetime):
    date_format = "%Y-%m-%d %H:%M:%S"
    expected_date_format = "%Y-%m-%dT%H:%M:%SZ"
    random_date, _, _ = random_datetime
    random_date_str = random_date.strftime(date_format)
    expected = random_date.strftime(expected_date_format)
    date_obj = datetime.strptime(random_date_str, date_format)
    assert to_iso8601(
        date_obj, t=True, z=True) == expected, 'iso8601 TZ format is not working as expected'


def test_to_iso8601_T(random_datetime):
    date_format = "%Y-%m-%d %H:%M:%S"
    expected_date_format = "%Y-%m-%dT"
    random_date, _, _ = random_datetime
    random_date_str = random_date.strftime(date_format)
    expected = random_date.strftime(expected_date_format)
    date_obj = datetime.strptime(random_date_str, date_format)
    assert to_iso8601(
        date_obj, t=True, z=False) == expected, 'iso8601 T format is not working as expected'


def test_to_iso8601_Z(random_datetime):
    date_format = "%H:%M:%S"
    expected_date_format = "%H:%M:%SZ"
    random_date, _, _ = random_datetime
    random_date_str = random_date.strftime(date_format)
    expected = random_date.strftime(expected_date_format)
    date_obj = datetime.strptime(random_date_str, date_format)
    assert to_iso8601(
        date_obj, t=False, z=True) == expected, 'iso8601 Z format is not working as expected'


def test_is_intersected_disjoint(random_datetime):
    random, start, end = random_datetime
    obj_a = Demand(startAt=start, endAt=random)

    obj_b = Demand(startAt=random + timedelta(microseconds=1), endAt=end)
    assert not is_intersected(
        obj_a, obj_b), 'Disjoint datetimes should not be intersected!'


def test_is_intersected_join(random_datetime):
    random, start, end = random_datetime
    obj_a = Demand(startAt=start, endAt=random)

    obj_b = Demand(startAt=random - timedelta(microseconds=1), endAt=end)
    assert is_intersected(
        obj_a, obj_b), 'Join datetimes should be intersected!'


def test_is_intersected_strict_true(random_datetime):
    random, start, end = random_datetime
    obj_a = Demand(startAt=start, endAt=random)

    obj_b = Demand(startAt=random, endAt=end)
    assert is_intersected(
        obj_a, obj_b, strict=True), 'Join intervals by frontier are consider join when is strict is True!'


def test_is_intersected_strict_false(random_datetime):
    random, start, end = random_datetime
    obj_a = Demand(startAt=start, endAt=random)

    obj_b = Demand(startAt=random, endAt=end)
    assert not is_intersected(
        obj_a, obj_b), 'Join intervals by frontier are not join when is strict is false!'
