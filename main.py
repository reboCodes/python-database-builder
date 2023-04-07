from database_builder.tables import Table
from database_builder.database import Database

class User(Table):
    # TODO: fingure out a way to make these work, they aren't showing up in vars(self)
    id = ["serial", "primary key"]
    first_name = ["varchar(50)"]
    last_name = ["varchar(50)"]
    email = ["varchar(50)"]


class Workout(Table):
    def __init__(self):
        self.id = ["serial", "primary key"]
        self.name = ["varchar(50)"]
        # self.user_id = [User]
        super().__init__()


if __name__ == "__main__":
    # my_db = Database( "127.0.0.1", "gym_app", "python_user", "python_user")
    # my_db._drop_all_tables()

    # my_db.create_table(
    #     User()
    # )

    x = User()
    super(User, x).__init__()

    # for table in my_db.tables:
    #     table: Table
    #     print(table.id)

    # my_db.drop_table(
    #     User(),
    #     Workout()
    # )



