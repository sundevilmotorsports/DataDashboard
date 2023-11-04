from session import Session
import pandas as pd

#array that holds different sessions accessible by the day it occured
active_sessions = []
live_sessions = []
def add_session(new_session, live = False):
    if live:
        live_sessions.append(new_session)
        print("add session live")
        print(new_session.get_metadata()["Name"])
        
    else:
        active_sessions.append(new_session)
        print("add session new")
        print(new_session.get_metadata()["Name"])
        
# def method for getting
def get_names():
    """Returns an array with the strings of the "Name" column within the Metadata Dataframe for each session in the dashboard"""
    temp = []
    for i in active_sessions:
        temp.append(i.get_metadata()["Name"])
    return temp

def get_live_names():
    """Returns an array with the strings of the "Name" column within the Metadata Dataframe for each session in the dashboard that are defined as Live"""
    temp = []
    for i in live_sessions:
        temp.append(i.get_metadata()["Name"])

# def method for getting laps
def get_active_sessions():
    """Getter for the active_sessions array"""
    return active_sessions

def get_live_sessions():
    """Getter for the live active sessions array"""
    return live_sessions
