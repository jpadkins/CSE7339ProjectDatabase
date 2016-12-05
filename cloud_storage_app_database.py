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
                """ CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL,
                password_hash TEXT NOT NULL, salt TEXT NOT NULL,
                drive_token TEXT, dropbox_token TEXT, box_token TEXT) """
        self.__conn.cursor().execute(stmt)
        self.__conn.commit()
        stmt = \
               """ CREATE TABLE IF NOT EXISTS files
               (filename TEXT, data BLOB, key TEXT, user_id INTEGER,
               FOREIGN KEY(user_id) REFERENCES user(rowid)) """
        self.__conn.cursor().execute(stmt)
        self.__conn.commit()

    def __del__(self):
        self.__conn.close()

    # does the username exist in the database?
    def __username_exists(self, username):
        stmt = "SELECT rowid FROM users WHERE username=? LIMIT 1"
        c = self.__conn.cursor().execute(stmt, [username])
        return len(c.fetchall()) > 0

    # get a user id from the database
    def __get_user_id(self, username, password):
        if self.__username_exists(username):
            query = \
                    "SELECT rowid, password_hash, salt FROM users "\
                    "WHERE username=?"
            res = self.__conn.cursor().execute(query, [username])
            user_id, password_hash, salt = res.fetchall()[0]
            check_hash = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
            if password_hash == check_hash:
                return user_id
            else:
                return False
        else:
            return False

    # add a user to the database
    def add_user(self, username, password):
        if not self.__username_exists(username):
            salt = crypt.mksalt(crypt.METHOD_SHA512)
            password_hash = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
            stmt = "INSERT INTO users VALUES (?, ?, ?, NULL, NULL, NULL)"
            self.__conn.cursor().execute(stmt, [username, password_hash, salt])
            self.__conn.commit()
            return True
        else:
            return False

    # set the auth token in the database
    def set_auth_token(self, username, api, token):
        if self.__username_exists(username):
            key = {
                API.DRIVE : 'drive_token',
                API.DROPBOX : 'dropbox_token',
                API.BOX : 'box_token'
            }.get(api, None)
            if not (key == None):
                stmt = "UPDATE users SET ?=? WHERE username=?"
                self.__conn.cursor().execute(stmt, [key, token, username])
                self.__conn.commit()
                return True
            else:
                return False
        else:
            return False

    # get an auth token from the database
    def get_auth_token(self, username, api):
        if self.__username_exists(username):
            key = {
                API.DRIVE : 'drive_token',
                API.DROPBOX : 'dropbox_token',
                API.BOX : 'box_token'
            }.get(api, None)
            if not (key == None):
                query = "SELECT "+key+" FROM users WHERE username=?"
                res = self.__conn.cursor().execute(query, [username])
                return res.fetchone()[0]
            else:
                return False
        else:
            return False

    # add a locally stored file for a user
    def add_local_file_and_key(self, username, password, filename, data, key):
        user_id = self.__get_user_id(username, password)
        if user_id:
            stmt = "INSERT INTO files VALUES (?,?,?,?)"
            self.__conn.cursor().execute(stmt, [filename, memoryview(data),
                                                key, user_id])
            self.__conn.commit()
            return True
        else:
            return False

    # returns a locally stored file for a user
    def get_local_file_and_key(self, username, password, filename):
        user_id = self.__get_user_id(username, password)
        if user_id:
            stmt = "SELECT data, key FROM files WHERE filename=? and user_id=?"
            res = self.__conn.cursor().execute(stmt, [filename, user_id])
            return str(res.fetchone()[0])
        else:
            return False

    # returns a list of file names for a user
    def get_local_file_names(self, username, password):
        user_id = self.__get_user_id(username, password)
        if user_id:
            stmt = "SELECT filename FROM files WHERE user_id=?"
            res = self.__conn.cursor().execute(stmt, [user_id])
            return res.fetchall()[0]
        else:
            return False
