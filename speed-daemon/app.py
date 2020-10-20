import glob
import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


@st.cache(allow_output_mutation=True)
def load_data():
    df_list = []
    for filename in glob.glob("../speed-daemon/data/*.json"):
        with open(filename, "r") as f:
            df_list.append(pd.json_normalize(json.load(f)))
    return pd.concat(df_list, ignore_index=True)


def parse_data(df):
    df["download_mbps"] = df["download"] / 1000000.0
    df["upload_mbps"] = df["upload"] / 1000000.0
    df["timestamp"] = df["timestamp"].astype('datetime64[ns]')
    df["date"] = df.timestamp.dt.date
    return df


def plot_timeseries(df):
    fig, axs = plt.subplots(3,1)

    axs[0].plot(df["timestamp"], df["download_mbps"], '.')
    axs[0].set_title("Download Speed")
    axs[0].set_ylabel("Mbps")

    axs[1].plot(df["timestamp"], df["upload_mbps"], '.')
    axs[1].set_title("Upload Speed")
    axs[1].set_ylabel("Mbps")

    axs[2].plot(df["timestamp"], df["ping"], '.')
    axs[2].set_title("Ping")
    axs[2].set_xlabel("Date")
    axs[2].set_ylabel("ms")

    return fig


def main():
    data = load_data()
    data = parse_data(data)
    fig = plot_timeseries(data)
    sns.set_theme()
    st.pyplot(fig)


if __name__ == '__main__':
    main()