import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='Admin', dbname='postgres')
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        cursor.execute('CREATE DATABASE migrator_test')
        print('PostgreSQL migrator_test created')
    except psycopg2.Error:
        print('PostgreSQL migrator_test already exists')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
