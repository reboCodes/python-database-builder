from .database import Database

class Table:

    def __init__(self, database: Database):
        self.database = database

    def _create_table_sql(self, **args):
        for key, value in args:
            print(key)
            print(f"   {value}")

#     def old__init__(self):
#         # save the table name, add an '_' to the end if its a reserved name
#         self._name = (type(self).__name__).lower()
#         if self._name in reserved_table_names:
#             print(f"Table cannot be named '{self._name}'")
#             print("This name is a reserved word in Postgres")
#             self._name += "_"
#             print(f"Table renamed to {self._name}")
#         # store the sql field data
#         self._field_list = []
#         for key, value in vars(self).items():
#             if key[0] != "_":
#                 if len(value) > 2:
#                     print(f"Invalid number of arguments for field {key}")
#                     return
#                 field = {
#                     "name": key,
#                     "type": None,
#                     "parameters": None
#                 }

#                 if type(value[0]) != str:
#                     field["type"] = "serial"
#                     if value[0]._name[-1] != '_':
#                         field["parameters"] = f"references {value[0]._name[:-1]}_id"
#                     else:
#                         field["parameters"] = f"references {value[0]._name}id"
#                 else:
#                     field["type"] = value[0]

#                 if len(value) == 2:
#                     if not field:
#                         field["parameters"] += " " + value[1]
#                     else:
#                         field["parameters"] = value[1]

#                 self._field_list.append(field)
#         print(f"Table '{self._name}'")
#         for x in self._field_list:
#             print(f"   {x}")




# reserved_table_names = [
#     "all",
#     "analyse",
#     "analyze",
#     "and",
#     "any",
#     "array",
#     "as",
#     "asc",
#     "asymmetric",
#     "both",
#     "case",
#     "cast",
#     "check",
#     "collate",
#     "column",
#     "constraint",
#     "create",
#     "current_catalog",
#     "current_date",
#     "current_role",
#     "current_time",
#     "current_timestamp",
#     "current_user",
#     "default",
#     "deferrable",
#     "desc",
#     "distinct",
#     "do",
#     "else",
#     "end",
#     "except",
#     "false",
#     "fetch",
#     "for",
#     "foreign",
#     "from",
#     "grant",
#     "group",
#     "having",
#     "in",
#     "initially",
#     "intersect",
#     "into",
#     "is",
#     "isnull",
#     "join",
#     "leading",
#     "limit",
#     "localtime",
#     "localtimestamp",
#     "not",
#     "null",
#     "offset",
#     "on",
#     "only",
#     "or",
#     "order",
#     "placing",
#     "primary",
#     "references",
#     "returning",
#     "select",
#     "session_user",
#     "some",
#     "symmetric",
#     "table",
#     "then",
#     "to",
#     "trailing",
#     "true",
#     "union",
#     "unique",
#     "user",
#     "using",
#     "variadic",
#     "when",
#     "where",
#     "window",
#     "with"
# ]

