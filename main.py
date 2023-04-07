from database_builder.tables import Table
from database_builder.database import Database

class User(Table):
    def __init__(self):
        self.id = ["serial", "primary key"]
        self.first_name = ["varchar(50)"]
        self.last_name = ["varchar(50)"]
        self.email = ["varchar(50)"]
        super().__init__()

class Workout(Table):
    def __init__(self):
        self.id = ["serial", "primary key"]
        self.name = ["varchar(50)"]
        # self.user_id = [User]
        super().__init__()


if __name__ == "__main__":
    my_db = Database( "127.0.0.1", "gym_app", "python_user", "python_user")

    my_db.create_table(
        User(),
        Workout()
    )


    print(my_db.tables)


    # my_db.drop_table(
    #     User(),
    #     Workout()
    # )



