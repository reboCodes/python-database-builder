import psycopg2
from .tables import Table

class Database:
    def __init__(self, host = None, database = None, user = None, password = None):
        self.tables = []
        self._set_connection(host, database, user, password) # call the set_connection method to set the connection variable
        self.connect()
        self._fetch_table_names()

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
        # store a cursor in the instance
        self._new_cursor()
        # return self so you can call connect() while instanciating Database  
        return self
    
    # method to create tables in the database
    def create_table(self, *args):
        for arg in args:
            # check if args are of type Table
            if not issubclass(type(arg), Table):
                print(f"create_table() only takes type: <Table>")
                return
            # treat args as type Table
            arg: Table

            # TODO: figure out a way to call the table init function

            if arg._table_name in self.tables:
                print(f"Table '{arg._table_name}' already exists." )
                continue
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
        
            # cache table
            self.tables.append(arg)

    def drop_table(self, *args):
        for arg in args:
            # check if arg is type Table
            if not issubclass(type(arg), Table):
                print(f"create_table() only takes type: <Table>")
                return
            # treat args as type Table
            arg: Table
            # if table does not exist, continue to next iteration
            if not arg._table_name in self.tables:
                print(f"Table {arg._table_name} does not exist")
                continue
            # attempt to delete the table, throw an error if it fails
            try:
                sql = f"drop table if exists {arg._table_name}"
                self._cur.execute(sql)
                self._conn.commit()
                print(f"Dropped table {arg._table_name}")
            except Exception as err:
                print(f"Cound not drop table '{arg._table_name}'")
                print(err)


    # private:

    # method to set the connection variable
    def _set_connection(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    # method to create a cursor
    def _new_cursor(self):
        # create a cursor
        try:
            self._cur = self._conn.cursor()
        except Exception as err:
            print("Could not create database cursor.")
            print(err)
    
    # check if input is type Table
    def _is_table(self, input):
        return issubclass(type(input), Table)


    # drop all tables
    def _drop_all_tables(self):
        try:
            self._cur.execute("""
                SELECT 'DROP TABLE IF EXISTS "' || tablename || '" CASCADE;'
                FROM pg_tables
                WHERE schemaname = 'public';
            """)
            self._conn.commit()
            self.tables = []
            print("All tables dropped")
        except Exception as err:
            print("Error while dropping all tables")
            print(err)


    #
    # I don't think I need this..?
    #
    # method to cache table names on database object
    def _fetch_table_names(self):
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