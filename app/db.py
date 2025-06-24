import psycopg2

def get_connection():
  return psycopg2.connect(
    host="localhost",
    database="postgres",    
    user="postgres",
    password="admin" 
  )

def create_table():
  print("run")
  conn = get_connection()
  cur = conn.cursor()
  cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        note TEXT NOT NULL
    )
  """)
  conn.commit()
  cur.close()
  conn.close()

def insert_note(note):
  conn = get_connection()
  cur = conn.cursor()
  cur.execute("INSERT INTO notes (note) VALUES (%s)", (note,))
  conn.commit()
  cur.close()
  conn.close()

def get_all_notes():
  conn = get_connection()
  cur = conn.cursor()
  cur.execute("SELECT * FROM notes")
  notes = cur.fetchall()
  cur.close()
  conn.close()
  return notes

def delete_note_by_id(note_id):
  conn = get_connection()
  cur = conn.cursor()
  cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
  conn.commit()
  deleted = cur.rowcount > 0
  cur.close()
  conn.close()
  return deleted