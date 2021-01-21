import pandas as pd
from pandas.testing import assert_frame_equal

from speed_daemon import data


def test_parse_data_localization_off():
    """Test with no localization"""
    test_data = pd.DataFrame(
        [
            {
                "download": 1000000,
                "timestamp": "2020-10-12T03:09:18.231187Z",
                "upload": 1000000,
            }
        ]
    )
    test_result = data.parse_data(test_data)
    expected_result = pd.DataFrame(
        data=[
            {
                "_timestamp_string": "2020-10-12T03:09:18.231187Z",
                "date": pd.to_datetime("2020-10-12").date(),
                "day_of_week": "Monday",
                "download": 1000000,
                "download_mbps": 1.0,
                "hour_of_day": 3,
                "upload": 1000000,
                "upload_mbps": 1.0,
            }
        ],
    )
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-10-12T03:09:18.231187Z")])
    )
    assert_frame_equal(expected_result, test_result, check_like=True)


def test_parse_data_localization_on():
    """Test localization with CDT (UTC-0500)"""
    test_data = pd.DataFrame(
        [
            {
                "download": 1000000,
                "timestamp": "2020-10-12T03:09:18.231187Z",
                "upload": 1000000,
            }
        ]
    )
    test_result = data.parse_data(test_data, localization="US/Central")
    expected_result = pd.DataFrame(
        data=[
            {
                "_timestamp_string": "2020-10-12T03:09:18.231187Z",
                "date": pd.to_datetime("2020-10-11").date(),
                "day_of_week": "Sunday",
                "download": 1000000,
                "download_mbps": 1.0,
                "hour_of_day": 22,
                "upload": 1000000,
                "upload_mbps": 1.0,
            }
        ],
    )
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-10-12T03:09:18.231187Z")])
    )
    assert_frame_equal(expected_result, test_result, check_like=True)


def test_parse_data_localization_on_cst():
    """Test localization with CST (UTC-0600)"""
    test_data = pd.DataFrame(
        [
            {
                "download": 1000000,
                "timestamp": "2020-11-12T03:09:18.231187Z",
                "upload": 1000000,
            }
        ]
    )
    test_result = data.parse_data(test_data, localization="US/Central")
    expected_result = pd.DataFrame(
        data=[
            {
                "_timestamp_string": "2020-11-12T03:09:18.231187Z",
                "date": pd.to_datetime("2020-11-11").date(),
                "day_of_week": "Wednesday",
                "download": 1000000,
                "download_mbps": 1.0,
                "hour_of_day": 21,
                "upload": 1000000,
                "upload_mbps": 1.0,
            }
        ],
    )
    expected_result = expected_result.set_index(
        pd.DatetimeIndex([pd.to_datetime("2020-11-12T03:09:18.231187Z")])
    )
    assert_frame_equal(expected_result, test_result, check_like=True)
