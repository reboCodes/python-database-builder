from database_builder.tables import Table
from database_builder.database import Database

class User(Table):
    def __init__(self):
        self.id = ["serial", "primary key"]
        self.first_name = ["string"]
        self.last_name = ["string"]
        self.email = ["string"]
        super().__init__()

class Workouts(Table):
    def __init__(self):
        self.id = None


if __name__ == "__main__":
    # my_db = Database( "127.0.0.1", "gym_app", "gym_app_user", "gym_app")
    sadf = User()

