from database_builder.database import *

class User(Table):
    def __init__(self, database):
        super().__init__(database)

class Workout(Table):
    def __init__(self, database):
        super().__init__(database)


if __name__ == "__main__":
    
    my_db = Database( "127.0.0.1", "gym_app", "python_user", "python_user").connect()
    my_db._drop_all_tables()

    new_user = User(my_db)
    new_user.first_name = "Reggie"
    new_user.last_name = "Scerbo"
    new_user.email = "reggie.scerbo@gmail.com"
    new_user.save()

    # workout = Workout(my_db)
    # workout.user = new_user
    # workout.date = datetime.date.today()
    # workout.save()

