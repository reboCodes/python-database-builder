README
This is a Python package for creating and managing tables in a database. The package includes a base Table class that can be extended to create tables with custom columns. The package also includes a Database class for managing connections to the database.

Installation
To install the package, run the following command:

pip install database_builder


Usage
Here's an example of how to use the package to create and manage tables in a database:


from database_builder.database import *

class User(Table):
    def __init__(self, database):
        super().__init__(database)

class Workout(Table):
    def __init__(self, database):
        super().__init__(database)

if __name__ == "__main__":
    # Connect to the database
    my_db = Database("127.0.0.1", "my_db_name", "my_db_username", "my_db_password").connect()

    # Drop any existing tables
    my_db._drop_all_tables()

    # Create a new user
    new_user = User(my_db)
    new_user.first_name = "John"
    new_user.last_name = "Doe"
    new_user.email = "johndoe@example.com"
    new_user.save()

    # Create a new workout for the user
    workout = Workout(my_db)
    workout.user = new_user
    workout.workout_type = "Running"
    workout.date = "2023-04-11"
    workout.save()

In this example, we create two tables: User and Workout. We then create a new user, set some attributes, and save the user to the database. Finally, we create a new workout and associate it with the user we just created.

Contributing
Contributions are welcome! If you find a bug or have an idea for a new feature, please submit an issue or a pull request on GitHub.

License
This package is licensed under the MIT License. See the LICENSE file for more information.