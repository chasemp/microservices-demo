from flask import Flask, request, jsonify
from flask_jwt_extended import (
     JWTManager, jwt_required,
     get_jwt_identity
)
import jwt
import os

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["ADMIN_PASSWORD"] = os.getenv("ADMIN_PASSWORD")

jwt_manager = JWTManager(app)

  # In-memory data store
  datastore = {}

  # In-memory user store
  users = {
    "admin": app.config["ADMIN_PASSWORD"]
  }

def create_jwt(identity, algorithm):
    payload = {
        "identity": identity
    }

     secret_key = app.config["JWT_SECRET_KEY"]
     token = jwt.encode(payload, secret_key, algorithm=algorithm)
     return token

@app.route("/login", methods=["POST"])
def login():
     if not request.is_json:
         return jsonify({"msg": "Missing JSON in request"}), 400

     username = request.json.get("username", None)
     password = request.json.get("password", None)
     algorithm = request.json.get("algorithm", "HS256")

     if not username and not password:
         return jsonify({"msg": "Missing username or password parameter"}), 400

     if users.get(username) == password:
         access_token = create_jwt(username, algorithm)
         return jsonify(access_token=access_token), 200
     else:
         return jsonify({"msg": "Bad username or password"}), 403

@jwt_required
@app.route("/items", methods=["POST"])
def create_item():
    item = request.json
    id = item["id"]
    datastore[id] = item
    return jsonify(item), 201

@jwt_required
@app.route("/items/<id>", methods=["GET"])
def get_item(id):
      item = datastore[id]
      return jsonify(item)

@jwt_required
@app.route("/items/<id>", methods=["DELETE"])
def delete_item(id):
     del datastore[id]
     return "", 204

@app.route("/items/<id>", methods=["PUT"])
@jwt_required()
def update_item(id):
    item = request.json
    datastore[id] = item
    return jsonify(item)

if __name__ == "__main__":
    app.run(debug=True)

