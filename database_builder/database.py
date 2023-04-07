import psycopg2
from .tables import Table

class Database:
    def __init__(self, host = None, database = None, user = None, password = None):
        self.tables = []
        self._set_connection(host, database, user, password) # call the set_connection method to set the connection variable
        self.connect()

    # method to connect to the database
    def connect(self):
        # user psycopg to connect to database
        try:
            print("Establishing connection to Database.")
            self._conn = psycopg2.connect(
                host = self.host,
                database = self.database,
                user = self.user,
                password = self.password
            )
            print(f"Connected to database: {self.database}.")
        except Exception as err:
            print("Could not connect to database.")
            print(err)

        self._new_cursor()
        return self
    
    # method to create tables in the database
    def create_table(self, *args):
        for arg in args:
            # check if args are of type Table
            if issubclass(type(arg), Table):
                # treat args as type Table
                arg: Table
            else:
                print(f"create_table() only takes type: <Table>")
                return
            try:
                sql = f"create table if not exists {arg._table_name} ("
                for key, value in arg._sql_data.items():
                    sql += key
                    for val in value:
                        sql += f" {val}"
                    sql += ", "
                sql = sql[:-2] + ");"
                self._cur.execute(sql)
                self._conn.commit()
                print(f"Created table {arg._table_name}")

            except Exception as err:
                print(f"Could not create table {arg._table_name}")
                print(err)
        self._cache_tables()

    def drop_table(self, *args):
        for arg in args:
            # check if table exists
            sql = f"""
            select exists (
                select 1
                from   information_schema.tables
                where  table_schema = 'public'
                and    table_name = '{arg._table_name}'
            );"""
            self._cur.execute(sql)
            # if table does not exist, continue to next iteration
            if not self._cur.fetchone()[0]:
                print(f"Table {arg._table_name} does not exist")
                continue
            # attempt to delete the table, throw an error if it fails
            try:
                sql = f"drop table if exists {arg._table_name}"
                self._cur.execute(sql)
                self._conn.commit()
                print(f"Dropped table {arg._table_name}")
            except Exception as err:
                print(f"Cound not drop table {arg._table_name}")
                print(err)


    # private:

    # method to cache table names on database object
    def _cache_tables(self):
        self._cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE';
        """)
        # update table instance variable
        tables = []
        for table in self._cur.fetchall():
            tables.append(table[0])
        self.tables = tables

    # method to create a cursor
    def _new_cursor(self):
        # create a cursor
        try:
            self._cur = self._conn.cursor()
        except Exception as err:
            print("Could not create database cursor.")
            print(err)

    # method to set the connection variable
    def _set_connection(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password