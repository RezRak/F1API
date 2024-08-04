import sqlite3


def createdatabase():
    conn = sqlite3.connect('F1Database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seasons ( 
        year INTEGER PRIMARY KEY
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS races (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        year INTEGER, 
        race_name TEXT, 
        location TEXT, 
        date TEXT, 
        winner TEXT,
        FOREIGN KEY(year) REFERENCES seasons(year)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER,
        name TEXT,
        team TEXT,
        points INTEGER,
        FOREIGN KEY(year) REFERENCES seasons(year)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS race_results (
        race_id INTEGER,
        driver_id INTEGER,
        points INTEGER,
        FOREIGN KEY(race_id) REFERENCES races(id),
        FOREIGN KEY(driver_id) REFERENCES drivers(id)
    )
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    createdatabase()
    print('Database created successfully!')
