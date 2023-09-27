import pandas as pd

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
        'Date': [date],
        'Driver': [driver],
        'Car': [car],
        'Track': [track],
        'Name': [name][0],
        'Lap': [lap],
        'Time': [time],
        'Lon': [lon],
        'Lat': [lat]
    }
    new_session = Session(df, new_metadata)
    return new_session

