def connect_to_database(name='database.db'):
    import sqlite3
    return sqlite3.connect(name, check_same_thread=False)

def init_db(connection):
    cursor = connection.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE, 
    password TEXT NOT NULL
    )   
    ''') 
    
    connection.commit()

def add_user(connection, username, password):
    cursor = connection.cursor()
    query = 'INSERT INTO users (username, password) VALUES (?, ?)'
    cursor.execute(query, (username, password))
    connection.commit()

def get_user_by_username(connection, username):
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE username = ?' 
    cursor.execute(query, (username,))
    return cursor.fetchone()

# def get_password_by_username(connection, username):
#     cursor = connection.cursor()
#     query = 'SELECT password FROM users WHERE username = ?'
#     cursor.execute(query, (username,))
#     return cursor.fetchone()
# def get_password_by_username(connection, username):
#     cursor = connection.cursor()
#     query = 'SELECT username FROM users WHERE username = ?'
#     cursor.execute(query, (username,))
#     return cursor.fetchone()

def init_gadgdet_db(connection):

    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gadgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_url TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
    ''')
    connection.commit()

def add_gadget(connection,user_id, title, description, price,image_url = None):
    cursor = connection.cursor()
    query = '''INSERT INTO gadgets (user_id, title, description, price, image_url) VALUES (?, ?, ?, ?, ?)'''
    cursor.execute(query, (user_id, title,description, price, image_url))
    connection.commit()

def get_gadget(connection, gadget_id):
    cursor = connection.cursor()    
    query = '''SELECT * FROM gadgets WHERE id = ?'''
    cursor.execute(query, (gadget_id))
    return cursor.fetchone()
    

def get_user_gadget(connection, user_id):
    cursor = connection.cursor()
    query = '''SELECT * FROM gadgets WHERE user_id = ?'''
    cursor.execute(query, (user_id))
    return cursor.fetchall()

def get_all_gadgets(connection):
    cursor = connection.cursor()
    query = '''SELECT * FROM gadgets '''
    cursor.execute(query)
    return cursor.fetchall()

def init_comments_table(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gadget_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gadget_id) REFERENCES gadgets (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    connection.commit()
    

def add_comment(connection, gadget_id, user_id, text):
    cursor = connection.cursor()
    query = '''INSERT INTO comments (gadget_id, user_id, text) VALUES (?, ?, ?)'''
    cursor.execute(query, (gadget_id, user_id, text))#to secure sqli
    connection.commit()

def get_comments_for_gadget(connection, gadget_id):
    cursor = connection.cursor()
    query = '''
        SELECT  users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.gadget_id = ?
    '''
    cursor.execute(query, (gadget_id,))#to secure sqli
    return cursor.fetchall()