import pandas as pd
from pandas.testing import assert_frame_equal

from speed_daemon.app import parse_data


def test_parse_data():
    test_data = pd.DataFrame(
        [
            {
                "download": 1000000,
                "timestamp": "2020-10-12T03:09:18.231187Z",
                "upload": 1000000,
            }
        ]
    )
    test_result = parse_data(test_data)
    print(test_data)
    print(test_data.dtypes)
    expected_result = pd.DataFrame(
        [
            {
                "date": pd.to_datetime("2020-10-11").date(),
                "day_of_week": "Sunday",
                "download": 1000000,
                "download_mbps": 1.0,
                "hour_of_day": 21,
                "timestamp": pd.to_datetime("2020-10-11T21:09:18.231187Z").tz_localize(
                    None
                ),
                "upload": 1000000,
                "upload_mbps": 1.0,
            }
        ]
    )
    assert_frame_equal(expected_result, test_result, check_like=True)
