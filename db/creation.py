import sqlite3
import os


def get_db_folder():
    filename = __file__
    return os.path.dirname(filename)


def get_db_file():
    return os.path.join(get_db_folder(), "sqlite_db.db")


def get_connection():
    """
    create a database connection to a SQLite database
    """
    return sqlite3.connect(get_db_file())


def create_db():
    if os.path.exists(get_db_file()):
        ans = input("Delete database? [y|n]")
        if ans.lower()[0]=='y':
            os.remove(get_db_file())
        else:
            exit()
    conn = get_connection()
    with open(get_db_folder() + "/create_tables.sql") as fp:
        conn.executescript(fp.read())
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_db()
