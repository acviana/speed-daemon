from pandas.testing import assert_frame_equal
import pandas as pd
import pytest

from speed_daemon import data


@pytest.fixture
def default_input():
    return {
        "download": 1000000,
        "ping": 1000000,
        "timestamp": "2020-10-12T03:09:18.231187Z",
        "upload": 1000000,
    }


@pytest.fixture
def default_expected_response():
    return {
        "_timestamp_string": "2020-10-12T03:09:18.231187Z",
        "date": pd.to_datetime("2020-10-12").date(),
        "day_of_week": "Monday",
        "download": 1000000,
        "download_mbps": 1.0,
        "hour_of_day": 3,
        "ping": 1000000,
        "upload": 1000000,
        "upload_mbps": 1.0,
    }


def test_parse_data_with_null_values(default_input, default_expected_response):
    """Zero value for null data (no connection)"""
    default_input["download"] = None
    default_input["upload"] = None
    default_input["ping"] = None
    test_result = data.parse_data(pd.DataFrame([default_input]))

    default_expected_response["download"] = 0.0
    default_expected_response["download_mbps"] = 0.0
    default_expected_response["upload"] = 0.0
    default_expected_response["upload_mbps"] = 0.0
    default_expected_response["ping"] = 0.0
    expected_result = pd.DataFrame([default_expected_response])
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-10-12T03:09:18.231187Z")])
    )

    assert_frame_equal(test_result, expected_result, check_like=True)


def test_parse_data_localization_off(default_input, default_expected_response):
    """Test with no localization"""
    test_data = pd.DataFrame([default_input])
    test_result = data.parse_data(test_data)

    expected_result = pd.DataFrame([default_expected_response])
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-10-12T03:09:18.231187Z")])
    )

    assert_frame_equal(expected_result, test_result, check_like=True)


def test_parse_data_localization_on(default_input, default_expected_response):
    """Test localization with CDT (UTC-0500)"""
    test_data = pd.DataFrame([default_input])
    test_result = data.parse_data(test_data, localization="US/Central")

    default_expected_response["date"] = pd.to_datetime("2020-10-11").date()
    default_expected_response["day_of_week"] = "Sunday"
    default_expected_response["hour_of_day"] = 22
    expected_result = pd.DataFrame([default_expected_response])
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-10-12T03:09:18.231187Z")])
    )
    expected_result = expected_result.set_index(
        expected_result.index.tz_convert("US/Central")
    )

    assert_frame_equal(expected_result, test_result, check_like=True)


def test_parse_data_localization_on_cst(default_input, default_expected_response):
    """Test localization with CST (UTC-0600)"""
    default_input["timestamp"] = "2020-11-12T03:09:18.231187Z"
    test_data = pd.DataFrame([default_input])
    test_result = data.parse_data(test_data, localization="US/Central")

    default_expected_response["_timestamp_string"] = "2020-11-12T03:09:18.231187Z"
    default_expected_response["date"] = pd.to_datetime("2020-11-11").date()
    default_expected_response["day_of_week"] = "Wednesday"
    default_expected_response["hour_of_day"] = 21
    expected_result = pd.DataFrame([default_expected_response])
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-11-12T03:09:18.231187Z")])
    )
    expected_result = expected_result.set_index(
        expected_result.index.tz_convert("US/Central")
    )

    assert_frame_equal(expected_result, test_result, check_like=True)
