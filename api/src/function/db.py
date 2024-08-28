import pymysql
from flask import g
from function.loadconfig import config

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=config['DBHOST'],
            user=config['DBUSER'],
            password=config['DBPASS'],
            database=config['DBNAME'],
        )
    return g.db

def get_puredb():
    return pymysql.connect(
        host=config['DBHOST'],
        user=config['DBUSER'],
        password=config['DBPASS'],
        database=config['DBNAME'],
    )
    

def get_dbdict():
    if 'dbdict' not in g:
        g.dbdict = pymysql.connect(
            host=config['DBHOST'],
            user=config['DBUSER'],
            password=config['DBPASS'],
            database=config['DBNAME'],
            cursorclass=pymysql.cursors.DictCursor,
        )
    return g.dbdict