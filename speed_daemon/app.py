import datetime
import glob
import json
from json import JSONDecodeError
import time

import pandas as pd
import seaborn as sns
import streamlit as st

from speed_daemon import visualize


def load_data():
    df_list = []
    for filename in glob.glob("../speed-daemon/data/*.json"):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                data = {}  # Not sure why/how this works?
            df_list.append(pd.json_normalize(data))
    return pd.concat(df_list, ignore_index=True)


def parse_data(df, localization=None):
    """
    Parses the input data and enriches data.

    Adds the following rows:
        - ``download_mbps``: The ``download`` column divided by 1,000,000.

    TODO

    Args:
        df (pandas.DataFrame): The input dataframe from ``load_data``.
        localization (str): A localization string e.g. "US/East".

    Returns:
        (pandas.DataFrame): An enriched and parsed dataframe.
    """
    # Scale data properties
    df["download_mbps"] = df["download"] / 1000000.0
    df["upload_mbps"] = df["upload"] / 1000000.0

    # Add a timezone-aware datetime index
    a_index = pd.DatetimeIndex(pd.to_datetime(df["timestamp"]))
    df = df.set_index(a_index)
    if localization:
        df = df.set_index(df.index.tz_convert(localization))
    df = df.rename(columns={"timestamp": "_timestamp_string"})

    # Precompute datetime groupings
    df["date"] = df.index.date
    df["day_of_week"] = df.index.day_name()
    df["hour_of_day"] = df.index.hour
    return df


def get_summary_stats(df, days_of_week=False):
    output = {
        "download_mbps": df.download_mbps.agg(["count", "median", "mean", "std"]),
        "upload_mbps": df.upload_mbps.agg(["count", "median", "mean", "std"]),
        "ping": df.ping.agg(["count", "median", "mean", "std"]),
    }
    if days_of_week:

        # TODO: Something about how dates are set up are giving this error:
        #
        # Using categorical units to plot a list of strings that are all
        # parsable as floats or dates. If these strings should be
        # plotted as numbers, cast to the appropriate data type before
        # plotting.
        #
        # Reference: https://stackoverflow.com/questions/46304691/matplotlib-could-not-convert-string-to-float

        day_of_week_index = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        output["download_mbps"] = output["download_mbps"].reindex(day_of_week_index)
        output["upload_mbps"] = output["upload_mbps"].reindex(day_of_week_index)
        output["ping"] = output["ping"].reindex(day_of_week_index)
    return output


def main():
    load_and_parse_t1 = time.time()
    data = load_data()
    # TODO: Made the localization a environment variable
    data = parse_data(data, localization="US/Central")
    load_and_parse_t2 = time.time()
    load_and_parse_time = load_and_parse_t2 - load_and_parse_t1
    sns.set_theme()

    # Scale of Data
    date_list = data.date.unique()
    st.text(f"Analyzing {len(data):,} data points over {len(date_list)} days")
    st.text(f"Loaded {len(data):,} data points in {load_and_parse_time:0.2f}s")

    # Last Reading
    st.subheader("Last Reading")
    st.table(
        data[data.index == data.index.max()][["download_mbps", "upload_mbps", "ping"]]
    )

    # Today's Stats
    st.subheader("Last 24 Hours")
    # TODO: This is not right, do we want last 24 hours or today's data?
    today = data[data.date == datetime.datetime.today().date()]
    today_stats = get_summary_stats(today)
    st.table(today_stats)
    st.pyplot(visualize.plot_summary(df=today, stats=today_stats))

    # Overall Stats
    st.subheader("All Data")
    overall_stats = get_summary_stats(data)
    st.table(overall_stats)
    st.text(dir(data.index.values))
    st.pyplot(visualize.plot_summary(df=data, stats=overall_stats))
    st.pyplot(visualize.plot_histograms(df=data, stats=overall_stats))

    stats_by_date = get_summary_stats(data.groupby(data.index.values))

    # Boxplot Timeseries
    st.subheader("Data by Date")
    st.pyplot(visualize.plot_timeseries_summary(stats_by_date))

    # Boxplot by Day of Week
    st.subheader("Data by Day of Week")
    stats_by_day_of_week = get_summary_stats(
        data.groupby(data.day_of_week), days_of_week=True
    )
    st.pyplot(visualize.plot_timeseries_summary(stats_by_day_of_week))

    # Boxplot by Hour
    st.subheader("Data by Hour")
    stats_by_hour_of_day = get_summary_stats(data.groupby(data.hour_of_day))
    st.pyplot(visualize.plot_timeseries_summary(stats_by_hour_of_day))

    # Weekday Boxplot by Hour
    st.subheader("Weekday Data by Hour")
    # TODO: Move this to a parsing function. Add is_weekday field.
    weekday_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weekday_data = data[data.day_of_week.isin(weekday_list)]
    weekdat_stats_by_hour_of_day = get_summary_stats(
        data.groupby(weekday_data.hour_of_day)
    )
    st.pyplot(visualize.plot_timeseries_summary(weekdat_stats_by_hour_of_day))


if __name__ == "__main__":
    main()
