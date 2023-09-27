from session import Session
import pandas as pd

#array that holds different sessions accessible by the day it occured
active_sessions = []

def add_session(new_session):
    active_sessions.append(new_session)


# def method for getting

def get_names():
    temp = []
    for i in active_sessions:
        temp.append(i.get_metadata()["Name"])
    return temp

# def method for getting laps

def get_active_sessions():
    return active_sessions