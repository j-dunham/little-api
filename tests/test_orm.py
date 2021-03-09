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
        Author.get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER "
        "PRIMARY KEY AUTOINCREMENT, age INTEGER, "
        "name TEXT);"
    )
    assert (
        Book.get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER "
        "PRIMARY KEY AUTOINCREMENT, author_id INTEGER, "
        "published INTEGER, title TEXT);"
    )
    for table in ("author", "book"):
        assert table in db.tables


def test_table_save(db, Author):
    db.create(Author)

    author = Author(name="Bob Smith", age=20)
    assert author.name == "Bob Smith"
    assert author.age == 20
    assert author.id is None
    assert author.get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [20, "Bob Smith"],
    )
    db.save(author)

    assert author.id is not None


def test_query_all_table_rows(db, Author):
    db.create(Author)
    bob = Author(name="Bob Smith", age=20)
    sally = Author(name="Sally Smith", age=21)
    db.save(bob)
    db.save(sally)
    authors = db.all(Author)

    assert Author.get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"],
    )
    assert len(authors) == 2
    assert type(authors[0]) == Author
    assert {a.age for a in authors} == {20, 21}
    assert {a.name for a in authors} == {"Bob Smith", "Sally Smith"}


def test_get_single_result(db, Author):
    db.create(Author)
    bob = Author(name="Bob Smith", age=20)
    sally = Author(name="Sally Smith", age=21)
    db.save(bob)
    db.save(sally)
    authors = db.get(Author, name="Sally Smith")

    assert Author.get_filtered_select(name="Sally Smith") == (
        "SELECT id, age, name FROM author WHERE name = ?;",
        ["id", "age", "name"],
        ["Sally Smith"],
    )
    assert len(authors) == 1
    assert authors[0].name == "Sally Smith"
    assert authors[0].id == 2


def test_get_no_result(db, Author):
    db.create(Author)
    bob = Author(name="Bob Smith", age=20)
    sally = Author(name="Sally Smith", age=21)
    db.save(bob)
    db.save(sally)
    authors = db.get(Author, id=10)

    assert Author.get_filtered_select(id=10) == (
        "SELECT id, age, name FROM author WHERE id = ?;",
        ["id", "age", "name"],
        [10],
    )
    assert len(authors) == 0


def test_foreign_key_result(db, Book, Author):
    db.create(Author)
    db.create(Book)

    bob = Author(name="Bob", age=50)
    book = Book(title="Bob's Book", published=True, author=bob)
    db.save(bob)
    db.save(book)

    books = db.get(Book, title="Bob's Book")
    assert len(books) == 1
    assert books[0].author.name == "Bob"
    assert books[0].author.age == 50


def test_db_update(db, Author):
    db.create(Author)
    author = Author(name="Bob Smith", age=20)
    db.save(author)
    author = db.get(Author, name="Bob Smith")[0]
    assert author.age == 20

    author.age = 50
    db.update(author)
    author = db.get(Author, name="Bob Smith")[0]
    assert author.age == 50


def test_db_delete(db, Author):
    db.create(Author)
    author = Author(name="Bob Smith", age=20)
    db.save(author)
    db.delete(author)

    author = db.get(Author, id=author.id)
    assert not author
