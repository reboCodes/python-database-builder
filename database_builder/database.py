import datetime
import psycopg2

class Database:
    def __init__(self, host = None, database = None, user = None, password = None):
        self.tables = {}

        self._set_connection(host, database, user, password) # call the set_connection method to set the connection variable
        self.connect()

    # method to connect to the database
    def connect(self):
        # use psycopg to connect to database
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
        self._cache_tables
        # return self so you can call connect() while instanciating Database  
        return self
    
    # method to create tables in the database
    # TODO: need to add in ability to create a reference to another table
    def create_table(self, table_name, column_data):
        print(column_data)

        # use postgres query to add the table to the database
        try:
            sql = f"create table if not exists {table_name} ("
            sql += "id serial primary key"
            for key, value in column_data.items():
                sql += f", {key} {value['data_type']}"
                if value["is_unique"]:
                    sql += " unique"
            sql += ");"
            self._cur.execute(sql)
            self._conn.commit()
            print(f"Created table {table_name}")
        except Exception as err:
            print(f"Could not create table {table_name}")
            print(err)
        # cache tables
        self._cache_tables()

    def drop_table(self, *args):
        for new_table in args:
            # check if arg is type Table
            if not issubclass(type(new_table), Table):
                print(f"create_table() only takes type: <Table>")
                return
            # treat args as type Table
            new_table: Table
            # if table does not exist, continue to next iteration
            if not new_table._name in self.tables:
                print(f"Table {new_table._name} does not exist")
                continue
            # attempt to delete the table, throw an error if it fails
            try:
                sql = f"drop table if exists {new_table._name}"
                self._cur.execute(sql)
                self._conn.commit()
                print(f"Dropped table {new_table._name}")
            except Exception as err:
                print(f"Cound not drop table '{new_table._name}'")
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

    # drop all tables
    def _drop_all_tables(self):
        try:
            self._cur.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            self._conn.commit()
            self._cache_tables()
            print("All tables dropped")
        except Exception as err:
            print("Error while dropping all tables")
            print(err)


    # method to cache table data on database object
    def _cache_tables(self):
        print("Caching Tables on Database object")
        # get table names from database 
        self._cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE';
        """)
        # update table instance variable
        tables_to_cache = []
        for table in self._cur.fetchall():
            if table[0] not in self.tables:
                tables_to_cache.append(table[0])
                self.tables[table[0]] = {}
        for table in tables_to_cache:
            self._cur.execute(f"""
                SELECT column_name, data_type,
                    CASE WHEN c.column_name IN
                                (SELECT column_name
                                FROM information_schema.constraint_column_usage
                                WHERE constraint_name IN
                                        (SELECT constraint_name
                                        FROM information_schema.table_constraints
                                        WHERE table_name = '{table}'
                                            AND constraint_type = 'UNIQUE'))
                            THEN 'YES'
                            ELSE 'NO'
                    END AS is_unique
                FROM information_schema.columns c
                WHERE table_name = '{table}';
            """)
            for column in self._cur.fetchall():
                is_unique = False
                if column[2] == "YES":
                    is_unique = True
                self.tables[table][column[0]] = {
                        "data_type": column[1],
                        "is_unique": is_unique
                    }
        print("Current tables in database:")
        print(self.tables)

    def _insert_row_(self, table, row_values):
        print("\n\ninserting data")
        print(table)
        sql = f"insert into {table} ("
        for column_name in row_values:
            sql += column_name + ", "
        sql = sql[:-2] + ") values ("
        for key, value in row_values.items():
            if isinstance(value, Table):
                #TODO: need a way to fetch the id of this object from the database
                print("cannot yet add a reference, feature coming soon!")
            else:
                sql += f"'{value}', "
        sql = sql[:-2] + ")"     
        try:
            self._cur.execute(sql)
            self._conn.commit()
        except Exception as err:
            print(f"Could not insert row into Table '{table}'")
            print(err)

class Table:

    def __init__(self, database: Database):
        # store the database object
        self._database = database
        # set the name of the table
        self._name = (type(self).__name__).lower()
        self._exclude_columns = []
        if self._name in reserved_table_names:
            print(f"Table cannot be named '{self._name}'")
            print("This name is a reserved word in Postgres")
            self._name += "_"
            print(f"Table renamed to {self._name}")

    def _cache_rows(self):
        print("\n\nCache Rows:")
        # get list of public objects from self
        self._column_data = {}
        self._row_values = {}
        self._database._cache_tables()
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if not callable(attr) and not attr_name.startswith('_') and attr_name not in self._exclude_columns:
                if attr_name in reserved_table_names:
                    attr_name += "_"
                if attr_name in self._database.tables:
                    print("reference found!")
                    if attr_name[-1] != "_":
                        attr_name += "_"
                    reference_name = attr_name + "id"
                    print(f"updated column from {attr_name} to {reference_name}")
                    self._column_data[reference_name] = {"data_type": f"integer references {attr_name} (id)", "is_unique": False} 
                    self._row_values[reference_name] = attr
                else:
                    self._column_data[attr_name] = {"data_type": py_to_pg_type(type(attr)), "is_unique": False}
                    self._row_values[attr_name] = attr


    def exclude(self, columns: list):
        for column in columns:
            if column not in self._exclude_columns:
                self._exclude_columns.append(column)

    def save(self, exclude_columns: list = []):
        print("Saving table to database")
        # TODO: maybe make a method that sets a unique identifier for a column in the table
        self._database._cache_tables()
        self.exclude(exclude_columns)
        self._cache_rows()
        if self._name not in self._database.tables:
            print(f"Table '{self._name}' does not exist, attempting to create it")
            self._database.create_table(self._name, self._column_data)
        else:
            print(f"Table '{self._name}' exists, checking columns")
            for key, value in self._row_values.items():
                if key not in self._database.tables[self._name]:
                    print(f"Field '{key}' was not found in Table '{self._name}' or in the exclusion list")
                    #TODO: write function in database to append table to add new column
                    # self._database._append_table()
        #TODO: insert row into table in database
        self._database._insert_row_(self._name, self._row_values)



def py_to_pg_type(py_type):
    type_map = {
        int: "integer",
        float: "double precision",
        bool: "boolean",
        str: "text",
        bytes: "bytea",
        datetime.datetime: "timestamp",
        datetime.date: "date",
        datetime.time: "time"
    }
    return type_map.get(py_type, "text")

reserved_table_names = [
    "all",
    "analyse",
    "analyze",
    "and",
    "any",
    "array",
    "as",
    "asc",
    "asymmetric",
    "both",
    "case",
    "cast",
    "check",
    "collate",
    "column",
    "constraint",
    "create",
    "current_catalog",
    "current_date",
    "current_role",
    "current_time",
    "current_timestamp",
    "current_user",
    "default",
    "deferrable",
    "desc",
    "distinct",
    "do",
    "else",
    "end",
    "except",
    "false",
    "fetch",
    "for",
    "foreign",
    "from",
    "grant",
    "group",
    "having",
    "in",
    "initially",
    "intersect",
    "into",
    "is",
    "isnull",
    "join",
    "leading",
    "limit",
    "localtime",
    "localtimestamp",
    "not",
    "null",
    "offset",
    "on",
    "only",
    "or",
    "order",
    "placing",
    "primary",
    "references",
    "returning",
    "select",
    "session_user",
    "some",
    "symmetric",
    "table",
    "then",
    "to",
    "trailing",
    "true",
    "union",
    "unique",
    "user",
    "using",
    "variadic",
    "when",
    "where",
    "window",
    "with"
]

