import inspect
import sqlite3

SQLITE_TYPE_MAP = {
    int: "INTEGER",
    float: "REAL",
    str: "TEXT",
    bytes: "BLOB",
    bool: "INTEGER",
}


class Database:
    def __init__(self, path):
        self.conn = sqlite3.Connection(path)

    def create(self, table):
        self.conn.execute(table.get_create_sql())

    @property
    def tables(self):
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table';"
        ).fetchall()
        return [row[0] for row in rows]

    def save(self, instance):
        sql, values = instance.get_insert_sql()
        inserted_id = self.conn.execute(sql, values)
        instance._column_data["id"] = inserted_id
        self.conn.commit()


class Table:
    def __init__(self, **kwargs):
        self._column_data = {"id": None}
        # stores columns in _column_data
        for key, value in kwargs.items():
            self._column_data[key] = value

    def __getattribute__(self, key):
        # avoid recursion error
        _column_data = super().__getattribute__("_column_data")
        if key in _column_data:
            return _column_data[key]
        return super().__getattribute__(key)

    @classmethod
    def get_create_sql(cls):
        create_sql = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        fields = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(f"{name} {field.sql_type}")
            elif isinstance(field, ForeignKey):
                fields.append(f"{name}_id INTEGER")
        fields = ", ".join(fields)
        name = cls.__name__.lower()
        return create_sql.format(name=name, fields=fields)

    def get_insert_sql(self):
        insert_sql = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields = []
        placeholders = []
        values = []
        # Get column definitions off of class
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                # Get values off of instance
                values.append(getattr(self, name))
                placeholders.append("?")
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
                placeholders.append("?")

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)
        table_name = cls.__name__.lower()
        sql = insert_sql.format(
            name=table_name, fields=fields, placeholders=placeholders
        )
        return sql, values


class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table
