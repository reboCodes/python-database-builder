import datetime
import psycopg2
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

class Api:
    routes = []
    app = Starlette()
        
    def start(host = "0.0.0.0", port = 8000):
        Api.app.routes.extend(Api.routes)
        uvicorn.run(Api.app, host = host, port = port)

class Database:
    def __init__(self, host = None, database = None, user = None, password = None):
        self._set_connection(host, database, user, password) # call the set_connection method to set the connection variable
        self.tables = {}
    
    # method to connect to the database
    def connect(self, drop = True):
        # use psycopg to connect to database
        try:
            # print("Establishing connection to Database.")
            self._conn = psycopg2.connect(
                host = self.host,
                database = self.database,
                user = self.user,
                password = self.password
            )
            # print(f"Connected to database: {self.database}.")
        except Exception as err:
            None
            # print("Could not connect to database.")
            # print(err)
        # store a cursor in the instance
        self._new_cursor()
        if drop:
            self._drop_all_tables()
        else:
            self._cache_tables
        # return self so you can call connect() while instanciating Database  
        return self
    
    # method to create tables in the database
    def _create_table(self, table_name, column_data):
        # use postgres query to add the table to the database

        # try:
        sql = f"create table if not exists {table_name} ("
        sql += "id serial primary key"
        for key, value in column_data.items():
            sql += f", {key} {value['data_type']}"
            if value["is_unique"]:
                sql += " unique"
        sql += f', constraint {table_name[:-1] if table_name.endswith("_") else table_name}_unique_constraint unique ('
        for column in column_data:
            sql += f"{column}, "
        sql = sql[:-2] + "));"
        # print(sql)
        self._cur.execute(sql)
        self._conn.commit()
        # print(f"Created table {table_name}")
        # except Exception as err:
        #     None
        #     print(f"Could not create table {table_name}")
        #     print(err)
        # cache tables
        self._cache_tables()

    def drop_table(self, *args):
        for new_table in args:
            # check if arg is type Api_Db_Object
            if not issubclass(type(new_table), Api_Db_Object):
                # print(f"create_table() only takes type: <Api_Db_Object>")
                return
            # treat args as type Api_Db_Object
            new_table: Api_Db_Object
            # if table does not exist, continue to next iteration
            if not new_table._name in self.tables:
                # print(f"Table {new_table._name} does not exist")
                continue
            # attempt to delete the table, throw an error if it fails
            try:
                sql = f"drop table if exists {new_table._name}"
                self._cur.execute(sql)
                self._conn.commit()
                # print(f"Dropped table {new_table._name}")
            except Exception as err:
                None
                # print(f"Cound not drop table '{new_table._name}'")
                # print(err)


    # private:

    # method to set the connection variable
    def _set_connection(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        Api_Db_Object._db_list.append(self)

    # method to create a cursor
    def _new_cursor(self):
        # create a cursor
        try:
            self._cur = self._conn.cursor()
        except Exception as err:
            None
            # print("Could not create database cursor.")
            # print(err)

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
            self.tables = {}
            # print("All tables dropped")
        except Exception as err:
            None
            # print("Error while dropping all tables")
            # print(err)


    # method to cache table data on database object
    def _cache_tables(self):
        # print("Caching Tables on Database object")
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
        # print("Current tables in database:")
        # print(self.tables)

    def _get_id(self, table_object) -> int:
        # build query
        sql = f"select id from {table_object._name} where "
        # print(table_object._row_values[0].items())
        for key, value in table_object._new_row.items():
            sql += f"{key} = "
            if type(value) in [int, float, bool]:
                sql += str(value) + " and "
            else:
                sql += f"'{value}' and "
        sql = sql[:-5] + ";"
        # make query
        try:
            self._cur.execute(sql)
            return self._cur.fetchone()[0]
        except Exception as err:
            None
            # print("Error making query for id")
            # print(err)

    # method to insert a new row into the database and return the id
    def _insert_row(self, table, row_values):
        # print("\ninserting row")
        sql = f"insert into {table} ("
        for column_name in row_values:
            sql += column_name + ", "
        sql = sql[:-2] + ") values ("
        for value in row_values.values():
            if isinstance(value, Api_Db_Object):
                sql += f"'{self._get_id(value)}', "
            elif value == None:
                sql += f"null, "
            else:
                sql += f"'{value}', "
        sql = sql[:-2] + ") returning id;"     
        # try:
        print(sql)
        self._cur.execute(sql)
        row_id = self._cur.fetchone()[0]
        self._conn.commit()
        row_values["id"] = row_id
        # except Exception as err:
        #     None
        #     print(f"Could not insert row into Table '{table}'")
        #     print(err)

class Api_Db_Object:

    _db_list = []
    _cache = {}

    def __init__(self, db_host = None):
        # store the database object
        if db_host:
            for db in self._db_list:
                if db.host == db_host:
                    self._database = db
        else:
            self._database = self._db_list[0]
        self._database :Database
        # initialize instance vairables
        self._column_data = {}
        self._row_values = []
        self._new_row = {}
        self._exclude_columns = []
        self._name = None
        # set the name of the table
        if self._name == None:
            self._name = self._clean_name = (type(self).__name__).lower()
            if self._name in reserved_table_names:
                # print(f"Table cannot be named '{self._name}'")
                # print("This name is a reserved word in Postgres")
                self._name += "_"
                # print(f"Table renamed to {self._name}")
        else:
            self._clean_name = self._name
        # add this route to the API
        Api.routes.append(Route("/" + self._clean_name, endpoint=self.get_all, methods=["GET"]))
        Api.routes.append(Route("/" + self._clean_name + "/{id}", endpoint=self.get, methods=["GET"]))
        
    async def get_all(self, request: Request):
        status, data = self.all(json=True)
        return JSONResponse({
            "status": status,
            "data": data
            })

    async def get(self, request: Request):
        status, data = self.where(json=True, id=request.path_params['id'])
        return JSONResponse({
            "status": status,
            "data": data
            })
    
    # this method sets the value of self._new_row based on the current public instance variables
    def _set_new_row(self):
        # print("\nCache Rows:")
        # get list of public objects from self
        self._new_row = {}
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)

            if not callable(attr_value) and not attr_name.startswith("_") and attr_name not in self._exclude_columns:

                attr_type = str(attr_value.__class__.__name__).lower()
                if attr_type in reserved_table_names:
                    attr_type += "_"

                if attr_name in reserved_table_names:
                    attr_name += "_"

                # create foreign key if needed
                if attr_type in self._database.tables:
                    # print(f"reference found! references: {attr_type}")
                    self._column_data[attr_name] = {"data_type": f"integer references {attr_type} (id)", "is_unique": False} 
                else:
                    self._column_data[attr_name] = {"data_type": py_to_pg_type(type(attr_value)), "is_unique": False}
                self._new_row[attr_name] = attr_value
                # print(self._new_row)

    # method to return the column data 
    def _columns(self):
        # try to return data cached on object
        # this data is cached during Api_Db_Object.save()
        if hasattr(self, "_column_data") and self._column_data:
            return self._column_data
        # try to return data cached on database
        # this data is cached during Db.Object.
        elif hasattr(self._database, f"tables") and self._database.tables[self._name]:
            return self._database.tables[self._name]
        else:
            return Exception

    # method to save a list of instance variable names that should not be set as table columns
    # call this before save or add a list in the save params
    # ex: User.exclude("weight", "age") or User.save(exclude_columns = ["weight", "age"])
    def exclude(self, *args):
        for column in args:
            if column not in self._exclude_columns:
                self._exclude_columns.append(column)

    def _create_object(self, row):
        new_obj = self.__class__()
        for key, value in row.items():
            setattr(new_obj, key, value)
        return new_obj

    # TODO: switch self._row_values to self._cache
    def where_cached(self, **args):
        if self._row_values == []:
            return
        results = []    
        for i, row in enumerate(self._row_values):
            for key, value in args.items():
                if key in row and row[key] == value:
                    if(i == len(self._row_values)-1):
                        results.append(self._create_object(row))
                else:
                    break
        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            return results
        else:
            return  None
        
    def all(self, json = False):
        sql = f"select * from {self._name}"
        # print(self._name)
        self._database._cur.execute(sql)
        if json:
            key_list = ["id"] + list(self._column_data.keys())
            result = []
            for row in self._database._cur.fetchall():
                item = {}
                for index, val in enumerate(row):
                    item[key_list[index]] = val
                result.append(item)
            return 200, result

    def where(self, json = False, **args):
        sql = f"select * from {self._name} where "
        for key, value in args.items():
            sql += f"{key} = "
            if type(value) in [int, float, bool]: 
                sql += str(value) + " and "
            else:
                    sql += f"'{value}' and "
        sql = sql[:-5] + ";"
        self._database._cur.execute(sql)
        db_response = self._database._cur.fetchall()
        if db_response == []:
            return 404, "Not Found"
        if json:
            key_list = ["id"] + list(self._column_data.keys())
            for row in db_response:
                item = {}
                for index, val in enumerate(row):
                    item[key_list[index]] = val
            return 200, item

    def save(self, exclude_columns: list = []):
        # print("Saving table to database")
        # TODO: maybe make a method that sets a unique identifier for a column in the table

        # set the values for the exclude_columns and the new_row
        self.exclude(exclude_columns)
        self._set_new_row()
        # if the table does not exist, create it
        if self._name not in self._database.tables:
            # print(f"Table '{self._name}' does not exist, attempting to create it")
            self._database._create_table(self._name, self._column_data)
        # if the table exists, add the new row
        # print(f"Table '{self._name}' exists, checking columns")
        for column_name in self._new_row:
            # make sure the columns exist
            if column_name not in self._database.tables[self._name]:
                None
                # print(f"Field '{column_name}' was not found in Table '{self._name}' or in the exclusion list")
                #TODO: write function in Database to append table to add new column
                # self._database._append_table()
        # add the row to the database
        self._database._insert_row(self._name, self._new_row)

def py_to_pg_type(py_type):
    type_map = {
        None: "NULL",
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

