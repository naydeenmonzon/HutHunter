from contextlib import contextmanager, ContextDecorator
from mysql.connector.connection import errors
import mysql.connector
import logging

formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s',datefmt="%Y-%b-%d %H:%M:%S")
logger = logging.getLogger(__name__)
eh = logging.FileHandler("C:/Users/Administrator/Documents/Projects/www/naydeenmonzon/PythonProjects/HutExplorer/Log/Logerror.log")
eh.setLevel(logging.ERROR)
eh.setFormatter(formatter)
# fh = logging.StreamHandler()
# fh.setLevel(logging.DEBUG)
logger.addHandler(eh)

class MySQLcnx(ContextDecorator):    
    @contextmanager
    def open_db(database:str):
        cnx = mysql.connector.connect(username='root', password='', database=database, host='localhost', autocommit=True)
        cursor = cnx.cursor()
        try:
            yield cursor
        except errors.Error as error:
            logger.error(error)
        finally: cnx.close()
    
    def fetch_all(database:str, table:str):
        
        with MySQLcnx.open_db(database) as cursor:
            cursor.execute(f'SELECT * FROM {table}')
            logger.debug(cursor.fetchall())

    def fetch_columns(database:str, table:str):
        
        with MySQLcnx.open_db(database) as cursor:
            cursor.execute(f'SELECT COLUMN_NAME, EXTRA from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME="{table}" and EXTRA="" ORDER BY ordinal_position')
            columns = cursor.fetchall()
            return [column[0] for column in columns]

    def post(database:str, table:str, query:tuple):
        
        columns = MySQLcnx.fetch_columns(database,table)
        value = ['%s' for i in range(len(columns))]
        statement = f"INSERT IGNORE INTO {table} ({', '.join(columns)}) VALUES ({', '.join(value)})"
        with MySQLcnx.open_db(database) as cursor:
            cursor.execute(statement,query)
            logger.debug(cursor.rowcount)

    def post_all(database:str, table:str, query_list:list[tuple]):
        columns = MySQLcnx.fetch_columns(database,table)
        value = ['%s' for i in range(len(columns))]
        statement = f"INSERT IGNORE INTO {table} ({', '.join(columns)}) VALUES ({', '.join(value)})"
        with MySQLcnx.open_db(database) as cursor:
            cursor_count = 0
            for query in query_list:
                cursor.execute(statement,query)
                cursor_count += int(cursor.rowcount)
            logger.debug(F'MYSQL: {cursor_count} posted to TABLE: {table}')
   