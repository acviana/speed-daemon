import glob
import json
from json import JSONDecodeError

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


@st.cache(allow_output_mutation=True)
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


def main():
    data = load_data()
    data = parse_data(data)
    date_list = data.date.unique()
    st.text(f"Analyzing {len(data)} data points over {len(date_list)} days")

    sns.set_theme()
    st.pyplot(plot_histograms(data))
    st.pyplot(plot_timeseries(data))

    # Boxplot Timeseries
    download_by_day = [data[data.date == date].download_mbps for date in date_list]
    upload_by_day = [data[data.date == date].upload_mbps for date in date_list]
    ping_by_day = [data[data.date == date].ping for date in date_list]
    st.pyplot(plot_boxplot_set(download_by_day, upload_by_day, ping_by_day))

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
