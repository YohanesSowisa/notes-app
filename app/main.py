import jwt
import datetime
from flask import Flask, request, jsonify
from functools import wraps
from db import (
    create_notes_table,
    create_users_table,
    register_user,
    get_user_by_username,
    insert_note,
    get_all_notes,
    get_all_users,
    delete_note_by_id,
    patch_note_by_id
)

app = Flask(__name__)

create_notes_table()
create_users_table()

@app.route("/users", methods=["GET"])
def get_users():
    users_data = get_all_users()
    result = [{"id": id, "username": username, "role": role} for (id, username, role) in users_data]
    return jsonify(result), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    if not username or not password:
      return jsonify({"message": "Username dan/atau password wajib diisi"}), 400
    
    success = register_user(username, password, role = 'user' if not role else role)
    if success:
      return jsonify({"message": "Registrasi berhasil"}), 201
    else:
      return jsonify({"message": "Username sudah digunakan atau error lain"}), 409


SECRET_KEY = 'rahasia_super_aman'


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = get_user_by_username(username)

    if user and user[2] == password:
        token = jwt.encode({
            'username': username,
            'role': user[3],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token}), 200

    return jsonify({'message': 'Username/password salah'}), 401
  
  
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            if bearer.startswith('Bearer '):
                token = bearer[7:]

        if not token:
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = {
              "username" : data['username'],
              "role" : data['role']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalid'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


@app.route("/notes", methods=["POST"])
@token_required
def post_notes(current_user):
    
    data = request.get_json()
    note = data.get('note')
    insert_note(note, current_user)
    
    if not note:
      return jsonify({"message": "Catatan tidak boleh kosong"})
    else:
      return jsonify({'message': f'Catatan {note} berhasil disimpan oleh user {current_user["username"]}'})


@app.route("/notes", methods=["GET"])
@token_required
def get_notes(current_user):
    notes_data = get_all_notes(current_user)
    result = [
        {"id": id, "note": note, "created_by": created_by, "created_at": created_at}
        for (id, note, created_by, created_at) in notes_data
    ]
    return jsonify(result), 200


@app.route("/notes/<int:id>", methods=["DELETE"])
@token_required
def del_notes(current_user, id):
    success = delete_note_by_id(id, current_user)

    if success:
        return jsonify({"message": f"Catatan Dengan ID {id} Berhasil Dihapus"}), 200
    else:
        return jsonify({"message": f"Catatan Dengan ID {id} Tidak Ditemukan atau bukan milik Anda"}), 404


@app.route("/notes/<int:id>", methods=["PATCH"])
@token_required
def patch_notes(current_user, id):
    patch_note = request.get_json()

    patched = patch_note_by_id(id, patch_note, current_user)

    return jsonify({"message": patched})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
