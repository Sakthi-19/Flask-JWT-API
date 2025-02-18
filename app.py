from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Configure MongoDB Atlas
app.config["MONGO_URI"] = "mongodb+srv://sakthivel19:Sakthivel-19@cluster0.yfwkf.mongodb.net/flask?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Configure JWT
app.config["JWT_SECRET_KEY"] = 'a3f7e8b59c4d6748f8b0c7f3e8d9a12c74e5d8a4b0c7e9d3f5a2b6c8e7f1a9d3'
jwt = JWTManager(app)

# Collections
users_collection = mongo.db.users
templates_collection = mongo.db.templates

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"message": "Email already exists"}), 400
    users_collection.insert_one(data)
    return jsonify({"message": "User registered successfully"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"], "password": data["password"]})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    access_token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": access_token})

# Create a Template
@app.route('/template', methods=['POST'])
@jwt_required()
def create_template():
    user_id = get_jwt_identity()
    data = request.json
    data["user_id"] = user_id
    inserted = templates_collection.insert_one(data)
    return jsonify({"message": "Template created", "id": str(inserted.inserted_id)}), 201

# Get All Templates (User-Specific)
@app.route('/template', methods=['GET'])
@jwt_required()
def get_templates():
    user_id = get_jwt_identity()
    templates = list(templates_collection.find({"user_id": user_id}, {"user_id": 0}))
    return jsonify(templates)

# Get Single Template
@app.route('/template/<template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    user_id = get_jwt_identity()
    template = templates_collection.find_one({"_id": ObjectId(template_id), "user_id": user_id}, {"user_id": 0})
    if not template:
        return jsonify({"message": "Template not found"}), 404
    return jsonify(template)

# Update Template
@app.route('/template/<template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    user_id = get_jwt_identity()
    data = request.json
    updated = templates_collection.update_one({"_id": ObjectId(template_id), "user_id": user_id}, {"$set": data})
    if updated.modified_count == 0:
        return jsonify({"message": "Template not found or no changes made"}), 404
    return jsonify({"message": "Template updated"})

# Delete Template
@app.route('/template/<template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    user_id = get_jwt_identity()
    deleted = templates_collection.delete_one({"_id": ObjectId(template_id), "user_id": user_id})
    if deleted.deleted_count == 0:
        return jsonify({"message": "Template not found"}), 404
    return jsonify({"message": "Template deleted"})

if __name__ == '__main__':
    app.run(debug=True)
