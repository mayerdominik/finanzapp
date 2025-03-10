import pandas as pd

def extend_missing_data(data, interval = 'd'):
     # Create a complete time range with given frequency (d = day, h = hour, m = minute)
    complete_time_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq=interval)

    # Reindex the data to include the complete time range
    data_reindexed = data.reindex(complete_time_range)

    # make index a column
    data_reindexed.reset_index(inplace=True)

    missing_values = 0
    for i, row in data_reindexed.iterrows():
        # if current row has a value at 'Close_EUR' and the next row is missing, look for the next available value and count the missing values
        if not pd.isna(row['Close_EUR']):
            if missing_values > 0:
                prv_value = data_reindexed['Close_EUR'].iloc[i - missing_values - 1]
                nxt_value = row['Close_EUR']
                slope = (nxt_value - prv_value) / (missing_values + 1)
                for j in range(1, missing_values + 1):
                    data_reindexed['Close_EUR'].iloc[i - missing_values - 1 + j] = prv_value + slope * j

            missing_values = 0
        elif pd.isna(row['Close_EUR']):
            missing_values += 1

    return data_reindexed