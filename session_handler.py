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
    temp = []
    for i in active_sessions:
        temp.append(i.get_metadata()["Name"])
    return temp

def get_live_names():
    temp = []
    for i in live_sessions:
        temp.append(i.get_metadata()["Name"])
# def method for getting laps

def get_active_sessions():
    return active_sessions

def get_live_sessions():
    return live_sessions

def get_sessions_from_csv():
    pass
