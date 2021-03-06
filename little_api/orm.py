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
        self.conn.execute(table._get_create_sql())

    @property
    def tables(self):
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table';"
        ).fetchall()
        return [row[0] for row in rows]


class Table:
    @classmethod
    def _get_create_sql(cls):
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


class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table
