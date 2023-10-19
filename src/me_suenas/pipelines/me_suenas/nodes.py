"""
This is a boilerplate pipeline 'me_suenas_pipeline'
generated using Kedro 0.18.14
"""

import pandas as pd
import polars as pl
import datetime

def expand_locations_column(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([df.drop(['locations'], axis=1), df['locations'].apply(pd.Series)], axis=1)

def process_df_pl(df: pd.DataFrame) -> pd.DataFrame:
    # Convert Pandas DataFrame to Polars DataFrame
    df_pl = pl.DataFrame(df)
    
    # Convert every dict in the 'locations' column to a column in the df.
    processed_df_pl = (
        df_pl.drop("locations")
        .lazy()
        .join(
            df_pl
            .select(pl.col("locations").apply(lambda x: list(x.values()), return_dtype=pl.Object).alias("exploded"))
            .lazy()
            .explode("exploded")
            .select(["*", "exploded.*"])
        )
        .collect()
    )
    
    # Convert back to Pandas DataFrame
    return processed_df_pl.to_pandas()

def set_accuracy_level(accuracy_level: str) -> dict:
    # Define Distance_Margin
    # -----------------------
    # Create a DataFrame to hold various accuracy levels and their corresponding
    # specifications: decimal places, accuracy in meters, and coordinate notation.
    # This will help in understanding and setting the granularity of distance measurements
    # for further data processing.

    Distance_Margin = pd.DataFrame({
        'accuracy.level': ['1', '2', '3', '4'],
        'decimal places': [3, 4, 5, 6],
        'accuracy (m)': [111, 11.1, 1.11, 0.111],
        'coordinates': ['+/- 00.000', '+/- 00.0000','+/- 00.00000','+/- 00.000000']
    })
    # Setting 'accuracy.level' as the index for easier lookup and referencing.
    Distance_Margin.set_index('accuracy.level', inplace=True)
    accuracy_info = Distance_Margin.loc[accuracy_level].to_dict()
    print('Accuracy level set to', accuracy_level, 'which corresponds to an accuracy of +/-', accuracy_info['accuracy (m)'], 'meters.')

    return accuracy_info

"""
# Turn 'timestamp' to datetime
df_x['timestamp'] = pd.to_datetime(df_x['timestamp'], format='ISO8601')
df_y['timestamp'] = pd.to_datetime(df_y['timestamp'], format='ISO8601')

# Find earliest timestamp
earliest_x = df_x['timestamp'].min()
earliest_y = df_y['timestamp'].min()

# Print earliest timestamp
print('Earliest timestamp for', x, 'is', earliest_x)
print('Earliest timestamp for', y, 'is', earliest_y)

# Define start date
start_date = max(earliest_x, earliest_y)
print('\nStart date is', start_date)

# Define end date as the date of our first date
end_date = pd.Timestamp('2021-08-06 19:00:00')
print('End date is', end_date)
"""

def prepare_timestamp(df_x: pd.DataFrame, df_y: pd.DataFrame, first_date: pd.Timestamp, x_name: str, y_name: str):
    # Turn 'timestamp' to datetime
    df_x['timestamp'] = pd.to_datetime(df_x['timestamp'], format='ISO8601')
    df_y['timestamp'] = pd.to_datetime(df_y['timestamp'], format='ISO8601')

    # Find earliest timestamp
    earliest_x = df_x['timestamp'].min()
    earliest_y = df_y['timestamp'].min()

    # Print earliest timestamp
    print('Earliest timestamp for', x_name, 'is', earliest_x)
    print('Earliest timestamp for', y_name, 'is', earliest_y)

    # Define start date
    start_date = max(earliest_x, earliest_y)
    print('\nStart date is', start_date)

    # Define end date as the date of our first date
    end_date = first_date
    print('The date you both met officially is ', end_date)

    # Filter out timestamps outside of start and end dates
    df_x = df_x[(df_x['timestamp'] >= start_date) & (df_x['timestamp'] <= end_date)]
    df_y = df_y[(df_y['timestamp'] >= start_date) & (df_y['timestamp'] <= end_date)]

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
    df_norm_time_x['timestamp'] = df_norm_time_x['timestamp'].apply(round_datetime_to_nearest_margin, args=(time_margin,))

    df_norm_time_y = df_y.copy()
    df_norm_time_y['timestamp'] = df_norm_time_y['timestamp'].apply(round_datetime_to_nearest_margin, args=(time_margin,))
        
    return df_norm_time_x, df_norm_time_y

def preprocess_map_data_for_person(df: pd.DataFrame, person: str, accuracy_info: dict):
    distance_accuracy = accuracy_info['decimal places']

    df = df[['timestamp', 'latitudeE7', 'longitudeE7', 'accuracy', 'source']]
    df.rename(columns={'latitudeE7': 'latitude', 'longitudeE7': 'longitude'}, inplace=True)
    df['person'] = person
    df['latitude'] = df['latitude'] / 10**7
    df['longitude'] = df['longitude'] / 10**7
    df['latitude'] = df['latitude'].round(distance_accuracy)
    df['longitude'] = df['longitude'].round(distance_accuracy)
    df['coordinates'] = df['latitude'].astype(str) + ' ' + df['longitude'].astype(str)

    df = df[df['accuracy'] >= 0]
    df = df[df['source'] != 'UNKNOWN']
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df