import sqlite3

import pytest

from little_api.orm import Column, Database, ForeignKey, Table


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author


@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    return Book


def test_create_db():
    db = Database("./test.db")
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_table_create(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"
