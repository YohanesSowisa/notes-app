# import requests
# from flask import Flask, request, jsonify
# from db import create_table, insert_note, get_all_notes, delete_note_by_id

# app = Flask(__name__)

# count = 1
# notes = []

# @app.route('/notes', methods=['POST'])
# def post_notes():
#   global count, notes
#   user_input = request.get_json()

#   if not user_input or 'note' not in user_input:
#     return jsonify({"error": "Field 'note' Wajib Diisi"}, 400)
  
#   new_note = {
#     'id' : count,
#     'note' : user_input['note']
#   }

#   notes.append(new_note)
#   count += 1

#   return jsonify(new_note), 201


# @app.route('/notes', methods=['GET'])
# def get_notes():
#   return jsonify(notes), 200


# @app.route('/notes/<int:id>', methods=['DELETE'])
# def del_notes(id):
#   global notes

#   note_to_delete = next((n for n in notes if n['id'] == id), None)

#   if note_to_delete:
#     notes.remove(note_to_delete)
#     return jsonify({"message": f"Catatan Dengan ID {id} Berhasil Dihapus"}, 200)
#   else:
#     return jsonify({"message": f"Catatan Dengan ID {id} Tidak Ditemukan"}, 404)


# if __name__ == '__main__':
#   app.run(debug=True, host="0.0.0.0",port=5000)


import requests
from flask import Flask, request, jsonify
from db import create_table, insert_note, get_all_notes, delete_note_by_id, patch_note_by_id

app = Flask(__name__)

create_table()

@app.route('/notes', methods=['POST'])
def post_notes():
  user_input = request.get_json()

  if not user_input or 'note' not in user_input:
    return jsonify({"error": "Field 'note' Wajib Diisi"}), 400
  
  note = user_input['note']
  insert_note(note)

  return jsonify({"message": f"Catatan '{note}' berhasil disimpan"}), 201


@app.route('/notes', methods=['GET'])
def get_notes():
  notes_data = get_all_notes()
  result = [{"id": id, "note": note} for (id, note) in notes_data]
  return jsonify(result), 200


@app.route('/notes/<int:id>', methods=['DELETE'])
def del_notes(id):
  success = delete_note_by_id(id)

  if success:
    return jsonify({"message": f"Catatan Dengan ID {id} Berhasil Dihapus"}), 200
  else:
    return jsonify({"message": f"Catatan Dengan ID {id} Tidak Ditemukan"}), 4044
  
  
@app.route('/notes/<int:id>', methods=['PATCH'])
def patch_notes(id):
  patch_note = request.get_json()

  patched = patch_note_by_id(id, patch_note)

  return jsonify({"message": patched})

if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=5000)