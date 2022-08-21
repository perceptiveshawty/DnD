from flask import Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2


class User(UserMixin):
    def __init__(self, username, id, isDM):
        self.id = id
        self.username = username
        self.isDM = isDM

    def get(uid):
        username = get_username(uid)
        access = get_access_level(uid)
        return User(username, uid, access)


def validate_user(username, pw):
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()

    uid = get_user(username)

    hash_pw_sql = """
    SELECT password FROM users WHERE "userID" = (%s)
    """

    print(uid)

    cur.execute(hash_pw_sql, (uid,))
    hash_pw = cur.fetchone()[0]

    return check_password_hash(hash_pw, pw)


def get_user(username):
    # perform SQL query
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    get_user_sql = """SELECT "userID" FROM users WHERE username = (%s) """
    cur.execute(get_user_sql, (username,))
    uid = cur.fetchone()[0]

    return uid


def get_username(uid):
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    get_user_sql = """SELECT username FROM users WHERE "userID" = (%s) """
    cur.execute(get_user_sql, (uid,))
    username = cur.fetchone()[0]

    return username


def get_access_level(uid):
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    get_user_sql = """SELECT "isDM" FROM users WHERE "userID" = (%s) """
    cur.execute(get_user_sql, (uid,))
    isDM = cur.fetchone()[0]

    return isDM


def create_user(username, pw, isDM):
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()

    hash_pw = generate_password_hash(pw)

    dm_state = False

    if isDM:
        dm_state = True

    get_user_sql = """INSERT INTO users (username, password, "isDM") VALUES ((%s), (%s), (%s))"""
    cur.execute(get_user_sql, (username, hash_pw, dm_state))
    con.commit()

    return True


def get_dmID(uid):
    con = psycopg2.connect('dbname=csce310 user=postgres password=csce310team19 host=localhost')
    cur = con.cursor()
    get_user_sql = """SELECT "dmID" FROM dungeon_master WHERE "userID" = (%s) """
    cur.execute(get_user_sql, (uid,))
    dmID = cur.fetchone()[0]

    return dmID