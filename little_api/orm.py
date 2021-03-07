import inspect
import sqlite3
from typing import List, Type

SQLITE_TYPE_MAP = {
    int: "INTEGER",
    float: "REAL",
    str: "TEXT",
    bytes: "BLOB",
    bool: "INTEGER",
}


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

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in self._column_data:
            self._column_data[key] = value

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

    @classmethod
    def get_select_all_sql(cls):
        select_sql = "SELECT {fields} FROM {name};"
        table_name = cls.__name__.lower()
        fields = ["id"]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            if isinstance(field, ForeignKey):
                fields.append(f"{name}_id")
        sql = select_sql.format(fields=", ".join(fields), name=table_name)
        return sql, fields

    @classmethod
    def get_filtered_select(cls, **kwargs):
        sql, fields = cls.get_select_all_sql()
        sql = sql[:-1]
        values = []
        for idx, item in enumerate(kwargs.items()):
            key, value = item
            if idx == 0:
                sql += f" WHERE {key} = ?"
            else:
                sql += f" AND {key} = ?"
            values.append(value)
        sql += ";"
        return sql, fields, values


class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table: Table):
        self.table = table


class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.Connection(path)

    def create(self, table: Table):
        self.conn.execute(table.get_create_sql())

    @property
    def tables(self) -> List[Table]:
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table';"
        ).fetchall()
        return [row[0] for row in rows]

    def save(self, table: Table) -> None:
        sql, values = table.get_insert_sql()
        result = self.conn.execute(sql, values)
        table._column_data["id"] = result.lastrowid
        self.conn.commit()

    def generate_instances(self, rows, fields, table):
        instances = []
        for row in rows:
            instance = table()
            for field, value in zip(fields, row):
                # If foreign key create instance for it
                if "_id" in field:
                    field = field[:-3]
                    # Get column off class
                    fk = getattr(table, field)
                    value = self.get(fk.table, id=value)[0]
                setattr(instance, field, value)
            instances.append(instance)
        return instances

    def all(self, table: Type[Table]) -> List:
        sql, fields = table.get_select_all_sql()
        rows = self.conn.execute(sql).fetchall()
        instances = self.generate_instances(rows, fields, table)
        return instances

    def get(self, table, **kwargs):
        sql, fields, values = table.get_filtered_select(**kwargs)
        rows = self.conn.execute(sql, tuple(values)).fetchall()
        instances = self.generate_instances(rows, fields, table)
        return instances
