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