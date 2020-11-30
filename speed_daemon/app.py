import datetime
import glob
import json
from json import JSONDecodeError

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


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


def plot_timeseries(df):
    fig, axs = plt.subplots(3, 1)
    fig.tight_layout(pad=1.0)

    axs[0].plot(df["timestamp"], df["download_mbps"], ".")
    axs[0].set_title("Download Speed")
    axs[0].set_ylabel("Mbps")

    axs[1].plot(df["timestamp"], df["upload_mbps"], ".")
    axs[1].set_title("Upload Speed")
    axs[1].set_ylabel("Mbps")

    axs[2].plot(df["timestamp"], df["ping"], ".")
    axs[2].set_title("Ping")
    axs[2].set_xlabel("Date")
    axs[2].set_ylabel("ms")

    return fig


def plot_histograms(df, stats):
    bins = 25
    fig, axs = plt.subplots(3, 2)
    fig.tight_layout(pad=1.0)

    plot_histogram(
        ax=axs[0][0],
        data=df["download_mbps"],
        bins=bins,
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
        y_label="Downloads",
        x_label="Mbps",
    )
    plot_histogram(
        ax=axs[1][0],
        data=df["upload_mbps"],
        bins=bins,
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
        y_label="Upload",
        x_label="Mbps",
    )
    plot_histogram(
        ax=axs[2][0],
        data=df["ping"],
        bins=bins,
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
        y_label="Ping",
        x_label="ms",
    )

    plot_histogram(
        ax=axs[0][1],
        data=df["download_mbps"],
        bins=bins,
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
        x_label="Mbps",
        y_scale="log",
    )
    plot_histogram(
        ax=axs[1][1],
        data=df["upload_mbps"],
        bins=bins,
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
        x_label="Mbps",
        y_scale="log",
    )
    plot_histogram(
        ax=axs[2][1],
        data=df["ping"],
        bins=bins,
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
        x_label="ms",
        y_scale="log",
    )

    return fig


def plot_histogram(
    ax,
    data,
    bins,
    orientation="vertical",
    mean=None,
    std=None,
    y_label=None,
    x_label=None,
    y_scale="linear",
):
    ax.hist(data, bins=bins, orientation=orientation)
    if orientation == "vertical":
        ax.axvline(mean - std, linestyle=":")
        ax.axvline(mean, linestyle="--")
        ax.axvline(mean + std, linestyle=":")
    else:
        ax.axhline(mean - std, linestyle=":")
        ax.axhline(mean, linestyle="--")
        ax.axhline(mean + std, linestyle=":")
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_yscale(y_scale)


def plot_scatterplot(ax, x_data, y_data, mean, std, title, y_label, x_label=None):
    ax.plot(x_data, y_data, ".")
    ax.axhline(mean - std, linestyle=":")
    ax.axhline(mean, linestyle="--")
    ax.axhline(mean + std, linestyle=":")
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)


def plot_summary(df, stats):
    fig, axs = plt.subplots(3, 2)
    fig.tight_layout(pad=1.0)

    plot_scatterplot(
        ax=axs[0][0],
        x_data=df["timestamp"],
        y_data=df["download_mbps"],
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
        title="Download Speed",
        y_label="Mbps",
    )
    plot_scatterplot(
        ax=axs[1][0],
        x_data=df["timestamp"],
        y_data=df["upload_mbps"],
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
        title="Upload Speed",
        y_label="Mbps",
    )
    plot_scatterplot(
        ax=axs[2][0],
        x_data=df["timestamp"],
        y_data=df["ping"],
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
        title="Ping",
        y_label="ms",
        x_label="Date",
    )

    bins = 10
    plot_histogram(
        ax=axs[0][1],
        data=df["download_mbps"],
        bins=bins,
        orientation="horizontal",
        mean=stats["download_mbps"]["mean"],
        std=stats["download_mbps"]["std"],
    )
    plot_histogram(
        ax=axs[1][1],
        data=df["upload_mbps"],
        bins=bins,
        orientation="horizontal",
        mean=stats["upload_mbps"]["mean"],
        std=stats["upload_mbps"]["std"],
    )
    plot_histogram(
        ax=axs[2][1],
        data=df["ping"],
        bins=bins,
        orientation="horizontal",
        mean=stats["ping"]["mean"],
        std=stats["ping"]["std"],
    )

    fig.autofmt_xdate()

    return fig


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


def plot_mean_median_std(ax, data, data_type):
    ax.errorbar(data.index, "mean", yerr="std", marker="o", linestyle="", data=data)
    ax.plot(data.index, "median", marker="x", linestyle="", data=data)
    ax.set_title(data_type)
    if data_type in ["Download", "Upload"]:
        ax.set_ylabel("Mbps")
    elif data_type == "Ping":
        ax.set_ylabel("ms")


def plot_timeseries_summary(df):
    fig, axs = plt.subplots(3, 1)
    fig.tight_layout(pad=1.0)

    plot_mean_median_std(axs[0], df["download_mbps"], "Download")
    plot_mean_median_std(axs[1], df["upload_mbps"], "Upload")
    plot_mean_median_std(axs[2], df["ping"], "Ping")

    fig.autofmt_xdate()

    return fig


def main():
    data = load_data()
    data = parse_data(data)
    sns.set_theme()

    # Scale of Data
    date_list = data.date.unique()
    st.text(f"Analyzing {len(data)} data points over {len(date_list)} days")

    # Last Reading
    st.subheader("Last Reading")
    st.table(data.iloc[0][["timestamp", "download_mbps", "upload_mbps", "ping"]])

    # Today's Stats
    st.subheader("Last 24 Hours")
    today = data[data.timestamp.dt.date == datetime.datetime.today().date()]
    today_stats = get_summary_stats(today)
    st.table(today_stats)
    st.pyplot(plot_summary(df=today, stats=today_stats))

    # Overall Stats
    st.subheader("All Data")
    overall_stats = get_summary_stats(data)
    st.table(overall_stats)
    st.pyplot(plot_summary(df=data, stats=overall_stats))
    st.pyplot(plot_histograms(df=data, stats=overall_stats))

    stats_by_date = get_summary_stats(data.groupby(data.timestamp.dt.date))

    # Boxplot Timeseries
    st.subheader("Data by Date")
    st.pyplot(plot_timeseries_summary(stats_by_date))

    # Boxplot by Day of Week
    st.subheader("Data by Day of Week")
    stats_by_day_of_week = get_summary_stats(
        data.groupby(data.day_of_week), days_of_week=True
    )
    st.pyplot(plot_timeseries_summary(stats_by_day_of_week))

    # Boxplot by Hour
    st.subheader("Data by Hour")
    stats_by_hour_of_day = get_summary_stats(data.groupby(data.hour_of_day))
    st.pyplot(plot_timeseries_summary(stats_by_hour_of_day))


if __name__ == "__main__":
    main()
