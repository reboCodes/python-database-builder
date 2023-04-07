
class Table:

    def __init__(self):

        for key, value in vars(self).items():
            print(key)
            for val in value:
                print(f"   {val}")

        self.table_name = type(self).__name__ + "s"



    def insert(self):
        for key, value in self.variables.items():
            if key != "id" and value == None:
                print("Insert failed:")
                print(f"{type(self).__name__} is missing one or more values\n")
                return
            
        sql = f"insert into {self.table_name} ("
        for var in self.variables.keys():
            sql += var + ", "
        print(sql[:-2])


    # set the values on the server but don't add them to the database
    # takes a diction of values or individual arguments
    def cache_values(self, dict = None, **kargs):
        for key, value in dict:
            setattr(self, key, value)
        for key, value in kargs:
            setattr(self, key, value)

    # get values from the database based on one of more arguments
    def fetch_values(self, **kargs):
        for key, value in kargs:
            # TODO
            return

