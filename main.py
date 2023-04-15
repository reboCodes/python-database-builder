from database_builder.database import *

class User(Table):
    def set_user(self, first_name, last_name, email, age):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.age = age

class Workout(Table):
    def set_workout(self, user, name, date):
        self.user = user
        self.name = name
        self.date = date

if __name__ == "__main__":
    
    my_db = Database( "127.0.0.1", "gym_app", "python_user", "python_user").connect()
    my_db._drop_all_tables()

    new_user1 = User(my_db)
    new_user1.set_user("Reggie", "Scerbo", "reggie.scerbo@gmail.com", 24)
    new_user1.save()

    new_user = User(my_db)
    new_user.set_user("Bob", "Jonson", "bob.jon@gmail.com", 24)
    new_user.save()

    new_workout = Workout(my_db)
    new_workout.set_workout(new_user1, "Back Day", datetime.date.today())
    new_workout.save()