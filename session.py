import pandas as pd
import pickle

class Session():
    def __init__(self, data:pd.DataFrame, metadata:pd.DataFrame):
        #data frame for the raw data from the box
        self.logger_data = data
        #data frame with the corresponding metadata
        self.logger_metadata = metadata

    def get_dataframe(self):
        return self.logger_data

    def get_metadata(self):
        return self.logger_metadata

# add a session to the workspace
def set_session(df, time, lap, lat, lon, name, date, driver, car, track):
    new_metadata = {
        'Date': [date][0],
        'Driver': [driver][0],
        'Car': [car][0],
        'Track': [track][0],
        'Name': [name][0],
        'Lap': [lap][0],
        'Time': [time][0],
        'Lon': [lon][0],
        'Lat': [lat][0]
    }
    new_session = Session(df, new_metadata)
    with open(f"data/{name}.pkl", "wb") as f:
        pickle.dump(new_session, f)
    return new_session

