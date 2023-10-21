"""
This is a boilerplate pipeline 'me_suenas_pipeline'
generated using Kedro 0.18.14
"""

import pandas as pd
import datetime
from typing import Dict


def expand_locations_column(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat(
        [df.drop(["locations"], axis=1), df["locations"].apply(pd.Series)], axis=1
    )


def set_accuracy_level(accuracy_level: str) -> dict:
    # Define Distance_Margin
    # -----------------------
    # Create a DataFrame to hold various accuracy levels and their corresponding
    # specifications: decimal places, accuracy in meters, and coordinate notation.
    # This will help in understanding and setting the granularity of distance measurements
    # for further data processing.

    Distance_Margin = pd.DataFrame(
        {
            "accuracy.level": ["1", "2", "3", "4"],
            "decimal places": [3, 4, 5, 6],
            "accuracy (m)": [111, 11.1, 1.11, 0.111],
            "coordinates": [
                "+/- 00.000",
                "+/- 00.0000",
                "+/- 00.00000",
                "+/- 00.000000",
            ],
        }
    )
    # Setting 'accuracy.level' as the index for easier lookup and referencing.
    Distance_Margin.set_index("accuracy.level", inplace=True)
    accuracy_info = Distance_Margin.loc[accuracy_level].to_dict()
    print(
        "Accuracy level set to",
        accuracy_level,
        "which corresponds to an accuracy of +/-",
        accuracy_info["accuracy (m)"],
        "meters.",
    )

    return accuracy_info


def prepare_timestamp(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    first_date: pd.Timestamp,
    x_name: str,
    y_name: str,
):
    # Turn 'timestamp' to datetime
    df_x["timestamp"] = pd.to_datetime(df_x["timestamp"], format="ISO8601")
    df_y["timestamp"] = pd.to_datetime(df_y["timestamp"], format="ISO8601")

    # Find earliest timestamp
    earliest_x = df_x["timestamp"].min()
    earliest_y = df_y["timestamp"].min()

    # Print earliest timestamp
    print("Earliest timestamp for", x_name, "is", earliest_x)
    print("Earliest timestamp for", y_name, "is", earliest_y)

    # Define start date
    start_date = max(earliest_x, earliest_y)
    print("\nStart date is", start_date)

    # Define end date as the date of our first date
    end_date = first_date
    print("The date you both met officially is ", end_date)

    # Filter out timestamps outside of start and end dates
    df_x = df_x[(df_x["timestamp"] >= start_date) & (df_x["timestamp"] <= end_date)]
    df_y = df_y[(df_y["timestamp"] >= start_date) & (df_y["timestamp"] <= end_date)]

    # Reset index
    df_x.reset_index(drop=True, inplace=True)
    df_y.reset_index(drop=True, inplace=True)

    return df_x, df_y


def round_datetime_to_nearest_margin(tm: datetime, time_margin: int) -> datetime:
    if time_margin <= 0:
        raise ValueError("Time margin must be positive and non-zero.")

    discard = datetime.timedelta(
        minutes=tm.minute % time_margin,
        seconds=tm.second,
        microseconds=tm.microsecond,
    )
    tm -= discard
    if discard >= datetime.timedelta(minutes=time_margin / 2):
        tm += datetime.timedelta(minutes=time_margin)

    return tm


def normalize_timestamp(df_x: pd.DataFrame, df_y: pd.DataFrame, time_margin: int):
    df_norm_time_x = df_x.copy()
    df_norm_time_x["timestamp"] = df_norm_time_x["timestamp"].apply(
        round_datetime_to_nearest_margin, args=(time_margin,)
    )

    df_norm_time_y = df_y.copy()
    df_norm_time_y["timestamp"] = df_norm_time_y["timestamp"].apply(
        round_datetime_to_nearest_margin, args=(time_margin,)
    )

    return df_norm_time_x, df_norm_time_y


def preprocess_map_data_for_person(df: pd.DataFrame, accuracy_info: dict):
    df = df.copy()
    distance_accuracy = accuracy_info["decimal places"]

    df.rename(
        columns={"latitudeE7": "latitude", "longitudeE7": "longitude"}, inplace=True
    )
    df["latitude"] = df["latitude"] / 10**7
    df["longitude"] = df["longitude"] / 10**7
    df["latitude"] = df["latitude"].round(distance_accuracy)
    df["longitude"] = df["longitude"].round(distance_accuracy)
    df["coordinates"] = df["latitude"].astype(str) + "," + df["longitude"].astype(str)
    df["gmaps_url"] = "https://www.google.com/maps/place/" + df["coordinates"].astype(
        str
    )
    df.drop(
        [
            "latitude",
            "longitude",
        ],
        axis=1,
        inplace=True,
    )

    # Extract date and timefrom timestamp
    df["date"] = pd.to_datetime(df["timestamp"]).dt.strftime("%d-%m-%Y")
    df["time"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M:%S")

    df = df[df["accuracy"] >= 0]
    df = df[df["source"] != "UNKNOWN"]
    df.reset_index(drop=True, inplace=True)

    return df[
        ["date", "time", "coordinates", "accuracy", "source", "gmaps_url"]
    ].drop_duplicates()


def combine_records(df_x: pd.DataFrame, df_y: pd.DataFrame, name_x: str, name_y: str):
    df = pd.merge(
        df_x,
        df_y,
        on=["date", "time", "coordinates"],
        suffixes=("_" + name_x, "_" + name_y),
    )
    return df


def find_encounters(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    common_locations = df.copy()

    grouped = common_locations.groupby("date")

    # Create a dictionary to hold each day's data
    encounters = {}
    for name, group in grouped:
        encounters[name] = group.copy().drop_duplicates()
        print("Found encounters on", name)

    return encounters
