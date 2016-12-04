import sqlite3
import crypt
import hashlib
from enum import Enum

class API(Enum):
    DRIVE, DROPBOX, BOX = range(3)

class CloudStorageAppDatabase(object):
    def __init__(self, db_file='sqlite.db'):
        self.__conn=sqlite3.connect(db_file)
        stmt = \
                """ CREATE TABLE IF NOT EXISTS users
                (username TEXT NOT NULL, password_hash TEXT NOT NULL,
                salt TEXT NOT NULL, drive_token TEXT, drive_timestamp TIMESTAMP,
                dropbox_token TEXT, dropbox_timestamp TIMESTAMP,
                box_token TEXT, box_timestamp TIMESTAMP) """
        self.__conn.cursor().execute(stmt)
        self.__conn.commit()

    def __del__(self):
        self.__conn.close()

    # add a user to the database
    def add_user(self, username, password):
        key = (username,)
        stmt = "SELECT EXISTS (SELECT 1 FROM users WHERE username=? LIMIT 1)"
        c = self.__conn.cursor().execute(stmt, key)
        if not c.fetchone():
            salt = crypt.mksalt(crypt.METHOD_SHA512)
            password_hash = hashlib.sha512(salt+password).hexdigest()
            stmt = \
                   """ INSERT INTO users (username, password_hash, salt,
                   drive_token, drive_timestamp, dropbox_token,
                   dropbox_timestamp, box_token, box_timestamp) VALUES
                   (?,?,?,?,?,?,?,?,?) """
            self.__conn.cursor().execute(stmt, username, password_hash, salt,
                                         None, None, None, None, None, None)
            self.__conn.commit()

    # get a user id from the database
    def get_user_id(self, username, password):
        return True

    # set the auth token in the database
    def set_auth_token(self, user_id, api, token):
        return True

    # get an auth token from the database
    def get_auth_token(self, user_id, api):
        return True
