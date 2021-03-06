import os
import sqlite3

import pytest

from little_api.orm import Column, Database, ForeignKey, Table


@pytest.fixture
def db(path: str = "./test.db"):
    # Remove database if exists
    if os.path.exists(path):
        os.remove(path)
    db = Database(path)
    yield db


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    yield Author


@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    yield Book


def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_table_create(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"


def test_create_table(db, Author, Book):

    db.create(Author)
    db.create(Book)

    assert (
        Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER "
        "PRIMARY KEY AUTOINCREMENT, age INTEGER, "
        "name TEXT);"
    )
    assert (
        Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER "
        "PRIMARY KEY AUTOINCREMENT, author_id INTEGER, "
        "published INTEGER, title TEXT);"
    )
    for table in ("author", "book"):
        assert table in db.tables
