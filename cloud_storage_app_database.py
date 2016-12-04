import sqlite3
from enum import Enum

class API(Enum):
    DRIVE, DROPBOX, BOX = range(3)

class CloudStorageAppDatabase(object):
    def __init__(self, db_file='sqlite.db'):
        self.__conn=sqlite3.connect(db_file)
        stmt = \
                """ CREATE TABLE IF NOT EXISTS users
                (id INTEGER, username TEXT, password TEXT, salt TEXT,
                drive_token TEXT, drive_timestamp TEXT, dropbox_token TEXT,
                dropbox_timestamp TEXT, box_token TEXT, box_timestamp TEXT
                ) """
        self.__conn.cursor().execute(stmt)
        self.__conn.commit()

    def __del__(self):
        self.__conn.close()

    # add a user to the database
    def add_user(username, password):
        try:
            self.__conn.cursor().execute(stmt)

    # get a user id from the database
    def get_user_id(username, password):
        try:
            ...

    # set the auth token in the database
    def set_auth_token(user_id, api, token):
        ...

    # get an auth token from the database
    def get_auth_token(user_id, api):
        ...
