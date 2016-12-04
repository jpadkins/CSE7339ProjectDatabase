import sqlite3
import crypt
import hashlib
from enum import Enum

class API(Enum):
    DRIVE, DROPBOX, BOX = range(3)

class CloudStorageAppDatabase(object):
    def __init__(self, db_file='sqlite3.db'):
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

    # does the username exist in the database?
    def __username_exists(self, username):
        stmt = \
               "SELECT rowid FROM users WHERE username=\""+username+"\""\
               " LIMIT 1"
        c = self.__conn.cursor().execute(stmt)
        return len(c.fetchall()) > 0

    # add a user to the database
    def add_user(self, username, password):
        if not self.__username_exists(username):
            salt = crypt.mksalt(crypt.METHOD_SHA512)
            password_hash = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
            stmt = \
                   "INSERT INTO users (username, password_hash, salt,"\
                   "drive_token, dropbox_token, box_token) VALUES"\
                   "(\""+username+"\",\""+password_hash+"\",\""+salt+"\","\
                   "NULL, NULL, NULL)"
            self.__conn.cursor().execute(stmt)
            self.__conn.commit()
            return True
        else:
            return False

    # get a user id from the database
    def get_user_id(self, username, password):
        if self.__username_exists(username):
            query = \
                    "SELECT rowid, password_hash, salt FROM users "\
                    "WHERE username=\""+username+'\"'
            res = self.__conn.cursor().execute(query)
            user_id, password_hash, salt = res.fetchall()[0]
            check_hash = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
            if password_hash == check_hash:
                return user_id
            else:
                return False
        else:
            return False

    # set the auth token in the database
    def set_auth_token(self, user_id, api, token):
        key = {
            API.DRIVE : 'drive_token',
            API.DROPBOX : 'dropbox_token',
            API.BOX : 'box_token'
        }.get(api, None)
        if not (key == None):
            stmt = \
                   "UPDATE users SET \""+key+"\"=\""+token+"\" "\
                   "WHERE rowid="+str(user_id)
            self.__conn.cursor().execute(stmt)
            self.__conn.commit()
            return True
        else:
            return False

    # get an auth token from the database
    def get_auth_token(self, user_id, api):
        key = {
            API.DRIVE : 'drive_token',
            API.DROPBOX : 'dropbox_token',
            API.BOX : 'box_token'
        }.get(api, None)
        if not (key == None):
            query = "SELECT \""+key+"\" FROM users WHERE rowid="+str(user_id)
            res = self.__conn.cursor().execute(query)
            return res.fetchone()[0]
        else:
            return False
