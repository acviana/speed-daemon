import glob
import json

from sqlalchemy import create_engine
import pandas as pd

DATABASE_URI = "sqlite:///database/speed-deamon.db"
FILE_SEARCH_PATH = "../speed-daemon/data/*.json"


def write_to_db(df, database_uri, table):
    engine = create_engine(DATABASE_URI, echo=True)
    with engine.begin() as connection:
        df.to_sql(table, con=connection, if_exists="replace")


def build_database(file_search_path, database_uri):
    data_df = load_from_json(file_search_path=file_search_path)
    write_to_db(df=data_df, database_uri=database_uri, table="data")


def load_from_json(file_search_path):
    df_list = []
    for filename in glob.glob(file_search_path):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
            df_list.append(pd.json_normalize(data))
    return pd.concat(df_list, ignore_index=True)


def load_from_sql(database_uri):
    engine = create_engine(database_uri, echo=True)
    with engine.begin() as connection:
        return pd.read_sql("data", connection)


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
    # Replace NULLs with 0s where there was no connection
    df["download"] = df["download"].fillna(0.0)
    df["upload"] = df["upload"].fillna(0.0)
    df["ping"] = df["ping"].fillna(0.0)

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
    build_database(file_search_path=FILE_SEARCH_PATH, database_uri=DATABASE_URI)


if __name__ == "__main__":
    main()
