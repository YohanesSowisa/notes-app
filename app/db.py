import psycopg2

def get_connection():
    return psycopg2.connect(
        host="db",
        port=5432,
        database="postgres",
        user="postgres",
        password="admin",
    )


def create_notes_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
      """
      CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        note TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
      """
    )

    conn.commit()
    cur.close()
    conn.close()


def create_users_table():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS users")

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT DEFAULT 'user'
    )
  """
    )

    conn.commit()
    cur.close()
    conn.close()


def register_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role),
        )
        conn.commit()
        result = True
    except Exception as e:
        print("Gagal register:", e)
        conn.rollback()
        result = False
    finally:
        cur.close()
        conn.close()
        return result

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def insert_note(note, created_by):
    conn = get_connection()
    cur = conn.cursor()
    
    if note:
      cur.execute(
          "INSERT INTO notes (note, created_by) VALUES (%s, %s)", (note, created_by['username'])
      )
      
    conn.commit()
    cur.close()
    conn.close()


def get_all_notes(current_user):
    conn = get_connection()
    cur = conn.cursor()
    
    if current_user['role'] == 'admin':
      cur.execute("SELECT * FROM notes")
    else:
      cur.execute("SELECT * FROM notes WHERE created_by = %s", (current_user['username'],))
    
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return notes


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    # cur.execute("SELECT * FROM users")
    cur.execute("SELECT id, username, role FROM users")
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return notes


def delete_note_by_id(note_id, current_user):
    conn = get_connection()
    cur = conn.cursor()
    
    if current_user['role'] == 'admin':
      cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    else:
      cur.execute("DELETE FROM notes WHERE id = %s AND created_by = %s", (note_id, current_user['username']))
    
    conn.commit()
    deleted = cur.rowcount > 0
    cur.close()
    conn.close()
    return deleted


# def patch_note_by_id(id, patch, username):
#     conn = get_connection()
#     cur = conn.cursor()

#     if not len(patch["note"]) == 0:
#         if "note" in patch:
#             cur.execute("UPDATE notes SET note = %s WHERE id = %s AND created_by = %s", (patch["note"], id, username))
#             conn.commit()
#             if cur.statusmessage == "UPDATE 0":
#                 result = f"Catatan dengan id {id} tidak ada"
#             else:
#                 result = f"Isi catatan dengan id {id} diubah menjadi {patch['note']}"
#         else:
#             result = "Tidak ada data yang diubah"
#     else:
#         result = "Catatan tidak boleh kosong"

#     cur.close()
#     conn.close()
#     return result


def patch_note_by_id(id, patch, current_user):
    if "note" not in patch:
        return "Tidak ada data yang diubah"

    note = patch["note"]
    if not note.strip():
        return "Catatan tidak boleh kosong"

    conn = get_connection()
    cur = conn.cursor()

    if current_user['role'] == 'admin':
      cur.execute("UPDATE notes SET note = %s WHERE id = %s", (note, id))
    else:
      cur.execute("UPDATE notes SET note = %s WHERE id = %s AND created_by = %s", (note, id, current_user['username']))
    
    conn.commit()

    result = (
        f"Isi catatan dengan id {id} diubah menjadi {note}"
        if cur.rowcount > 0
        else f"Catatan dengan id {id} tidak ditemukan atau bukan milik Anda"
    )

    cur.close()
    conn.close()
    return result
