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


def parse_data(df):
    df["download_mbps"] = df["download"] / 1000000.0
    df["upload_mbps"] = df["upload"] / 1000000.0
    df["timestamp"] = df["timestamp"].astype("datetime64[ns]")
    df["date"] = df.timestamp.dt.date
    df["day_of_week"] = df.timestamp.dt.day_name()
    df["hour_of_day"] = df.timestamp.dt.hour
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


def plot_histograms(df):
    bins = 25
    fig, axs = plt.subplots(3, 2)
    fig.tight_layout(pad=1.0)

    axs[0][0].hist(df["download_mbps"], bins=bins)
    axs[0][0].set_xlabel("Mbps")
    axs[0][0].set_ylabel("Downloads")

    axs[1][0].hist(df["upload_mbps"], bins=bins)
    axs[1][0].set_xlabel("Mbps")
    axs[1][0].set_ylabel("Uploads")

    axs[2][0].hist(df["ping"], bins=bins)
    axs[2][0].set_xlabel("ms")
    axs[2][0].set_ylabel("Pings")

    axs[0][1].set_yscale("log")
    axs[0][1].hist(df["download_mbps"], bins=bins)
    axs[0][1].set_xlabel("Mbps")

    axs[1][1].set_yscale("log")
    axs[1][1].hist(df["upload_mbps"], bins=bins)
    axs[1][1].set_xlabel("Mbps")

    axs[2][1].set_yscale("log")
    axs[2][1].hist(df["ping"], bins=bins)
    axs[2][1].set_xlabel("ms")

    return fig


def plot_boxplot_set(download_data, upload_data, ping_data):
    fig, axs = plt.subplots(3, 1)
    fig.tight_layout(pad=1.0)

    axs[0].set_title("Download Speed")
    axs[0].boxplot(download_data, flierprops={"marker": "x"})
    axs[0].set_ylabel("Mbps")

    axs[1].set_title("Upload Speed")
    axs[1].boxplot(upload_data, flierprops={"marker": "x"})
    axs[1].set_ylabel("Mbps")

    axs[2].set_title("Ping")
    axs[2].boxplot(ping_data, flierprops={"marker": "x"})
    axs[2].set_ylabel("ms")

    return fig


def plot_scatterplot(ax, x_data, y_data, mean, std, title, y_label, x_label=None):
    ax.plot(x_data, y_data, ".")
    ax.axhline(mean - std, linestyle=":")
    ax.axhline(mean)
    ax.axhline(mean + std, linestyle=":")
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)


def plot_summary(df, stats):
    fig, axs = plt.subplots(3, 2)
    fig.tight_layout(pad=1.0)

    plot_scatterplot(
        axs[0][0],
        df["timestamp"],
        df["download_mbps"],
        stats["download_mbps"]["mean"],
        stats["download_mbps"]["std"],
        "Download Speed",
        "Mbps",
    )

    plot_scatterplot(
        axs[1][0],
        df["timestamp"],
        df["upload_mbps"],
        stats["upload_mbps"]["mean"],
        stats["upload_mbps"]["std"],
        "Upload Speed",
        "Mbps",
    )

    plot_scatterplot(
        axs[2][0],
        df["timestamp"],
        df["ping"],
        stats["ping"]["mean"],
        stats["ping"]["std"],
        "Ping",
        "ms",
        "Date",
    )

    bins = 10

    axs[0][1].hist(df["download_mbps"], bins=bins, orientation="horizontal")
    axs[0][1].axhline(stats["download_mbps"]["mean"], linestyle="--")
    axs[1][1].hist(df["upload_mbps"], bins=bins, orientation="horizontal")
    axs[1][1].axhline(stats["upload_mbps"]["mean"], linestyle="--")
    axs[2][1].hist(df["ping"], bins=bins, orientation="horizontal")
    axs[2][1].axhline(stats["ping"]["mean"], linestyle="--")

    return fig


def get_summary_stats(df):
    return {
        "download_mbps": df.download_mbps.agg(["count", "median", "mean", "std"]),
        "upload_mbps": df.upload_mbps.agg(["count", "median", "mean", "std"]),
        "ping": df.ping.agg(["count", "median", "mean", "std"]),
    }


def main():
    data = load_data()
    data = parse_data(data)
    date_list = data.date.unique()
    st.text(f"Analyzing {len(data)} data points over {len(date_list)} days")

    # Today Section
    today = data[data.timestamp.dt.date == datetime.datetime.today().date()]
    today_stats = get_summary_stats(today)
    st.table(today_stats)
    st.pyplot(plot_summary(today, stats=today_stats))

    daily_stats = get_summary_stats(data.groupby(data.timestamp.dt.date))

    # Next Section
    st.table(daily_stats["download_mbps"])
    st.table(daily_stats["upload_mbps"])
    st.table(daily_stats["ping"])

    sns.set_theme()
    st.pyplot(plot_histograms(data))
    st.pyplot(plot_timeseries(data))

    # Boxplot Timeseries
    download_by_date = [data[data.date == date].download_mbps for date in date_list]
    upload_by_date = [data[data.date == date].upload_mbps for date in date_list]
    ping_by_date = [data[data.date == date].ping for date in date_list]
    st.pyplot(plot_boxplot_set(download_by_date, upload_by_date, ping_by_date))

    # Boxplot by Day of Week
    day_of_week_list = data.day_of_week.unique()
    download_by_day_of_week = [
        data[data.day_of_week == day_name].download_mbps
        for day_name in day_of_week_list
    ]
    upload_by_day_of_week = [
        data[data.day_of_week == day_name].upload_mbps for day_name in day_of_week_list
    ]
    ping_by_day_of_week = [
        data[data.day_of_week == day_name].ping for day_name in day_of_week_list
    ]
    st.pyplot(
        plot_boxplot_set(
            download_by_day_of_week, upload_by_day_of_week, ping_by_day_of_week
        )
    )

    # Boxplot by Hour
    hour_list = data.hour_of_day.unique()
    download_by_hour = [
        data[data.hour_of_day == hour].download_mbps for hour in hour_list
    ]
    upload_by_hour = [data[data.hour_of_day == hour].upload_mbps for hour in hour_list]
    ping_by_hour = [data[data.hour_of_day == hour].ping for hour in hour_list]
    st.pyplot(plot_boxplot_set(download_by_hour, upload_by_hour, ping_by_hour))


if __name__ == "__main__":
    main()
