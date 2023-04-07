import psycopg2
from .tables import Table

class Database:
    def __init__(self, host = None, database = None, user = None, password = None):
        self.set_connection(host, database, user, password) # call the set_connection method to set the connection variable


    # method to set the connection variable
    def set_connection(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    # method to connect to the database
    def connect(self):
        # user psycopg to connect to database
        try:
            print("Establishing connection to Database.")
            self.conn = psycopg2.connect(
                host = self.host,
                database = self.database,
                user = self.user,
                password = self.password
            )
            print(f"Connected to database: {self.database}.")
        except Exception as err:
            print("Could not connect to database.")
            print(err)

        # create a cursor
        try:
            self.cur = self.conn.cursor()
        except Exception as err:
            print("Could not create database cursor.")
            print(err)
        
        # return the database
        return self
