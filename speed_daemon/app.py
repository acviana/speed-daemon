import datetime
import time

import seaborn as sns
import streamlit as st

from speed_daemon import (
    # TODO: Fix this namespacing; was too lazy to rename data dataframe
    data as data_tools,
    visualize,
)


def main():
    load_and_parse_t1 = time.time()
    data = data_tools.load_from_sql()
    # TODO: Made the localization a environment variable
    data = data_tools.parse_data(data, localization="US/Central")
    data_tools.write_to_db(data, "parsed_data")
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
    today_stats = data_tools.get_summary_stats(today)
    st.table(today_stats)
    st.pyplot(visualize.plot_summary(df=today, stats=today_stats))

    # Overall Stats
    st.subheader("All Data")
    overall_stats = data_tools.get_summary_stats(data)
    st.table(overall_stats)
    st.pyplot(visualize.plot_summary(df=data, stats=overall_stats))
    st.pyplot(visualize.plot_histograms(df=data, stats=overall_stats))

    stats_by_date = data_tools.get_summary_stats(data.groupby(data.index.values))

    # Boxplot Timeseries
    st.subheader("Data by Date")
    st.pyplot(visualize.plot_timeseries_summary(stats_by_date))

    # Boxplot by Day of Week
    st.subheader("Data by Day of Week")
    stats_by_day_of_week = data_tools.get_summary_stats(
        data.groupby(data.day_of_week), days_of_week=True
    )
    st.pyplot(visualize.plot_timeseries_summary(stats_by_day_of_week))

    # Boxplot by Hour
    st.subheader("Data by Hour")
    stats_by_hour_of_day = data_tools.get_summary_stats(data.groupby(data.hour_of_day))
    st.pyplot(visualize.plot_timeseries_summary(stats_by_hour_of_day))

    # Weekday Boxplot by Hour
    st.subheader("Weekday Data by Hour")
    # TODO: Move this to a parsing function. Add is_weekday field.
    weekday_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weekday_data = data[data.day_of_week.isin(weekday_list)]
    weekdat_stats_by_hour_of_day = data_tools.get_summary_stats(
        data.groupby(weekday_data.hour_of_day)
    )
    st.pyplot(visualize.plot_timeseries_summary(weekdat_stats_by_hour_of_day))


if __name__ == "__main__":
    main()
