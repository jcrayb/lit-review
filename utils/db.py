import sqlite3

db = "db.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

try:
    cur.execute(
        """CREATE TABLE papers(
        id VARCHAR(16),
        title TEXT,
        year INTEGER,
        authors TEXT,
        journal TEXT,
        keywords TEXT,
        relevance INTEGER,
        url TEXT
        )
    """
    )
except:
    pass

conn.close()
    

def is_hex_used(hex_):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()

        results = cur.execute("SELECT id FROM papers WHERE id = ?;", (hex_,)).fetchone()

    return True if len(results) > 0 else False

def get_results(hex_):
    print(hex_)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()

        results = cur.execute("SELECT * FROM papers WHERE id = ?;", (hex_,)).fetchall()

    return results

def add_result(hex_, data):
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()

        cur.execute('INSERT INTO papers VALUES  (?, ?, ?, ?, ?, ?, ?, ?);', (hex_, *data))
    return