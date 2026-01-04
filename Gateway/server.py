import os, gridfs, pika, json #grdfs is used for storing larger files in our mongodb, pika: used for interfacing with our queue(as we're gng to use rabbitmq service to stor eour msges)
from flask import Flask, request
from flask_pymongo import PyMongo #will use mongodb for storing our files
from auth import validate
from auth_svc import access
from storage import util

server= Flask(__name__)
server.config["MONGO_URI"]= os.environ.get("MONGO_URI","mongodb://host.minikube.internal:27017/videos")

mongo= PyMongo(server)

fs= gridfs.GridFS(mongo.db)

connection= pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("RABBITMQ_HOST","host.minikube.internal")))
channel= connection.channel()


import requests
from flask import request, jsonify

AUTH_SERVICE_URL = "http://auth-service:8000"


@server.route("/auth/register", methods=["POST"])
def register():
    resp = requests.post(
        f"{AUTH_SERVICE_URL}/register",
        json=request.get_json()
    )
    return jsonify(resp.json()), resp.status_code


@server.route("/auth/login", methods=["POST"])
def login():
    resp = requests.post(
        f"{AUTH_SERVICE_URL}/login",
        json=request.get_json()
    )
    return jsonify(resp.json()), resp.status_code


@server.route("/auth/protected", methods=["GET"])
def protected():
    headers = {
        "Authorization": request.headers.get("Authorization")
    }
    resp = requests.get(
        f"{AUTH_SERVICE_URL}/protected",
        headers=headers
    )
    return jsonify(resp.json()), resp.status_code


@server.route("/")
def root():
    return {"status": "Gateway is running"}


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err= validate.token(request)

    access= json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access)

            if err:
                return err
        return "file uploaded successfully", 200
    else:
        return "Not authorized", 401
    

@server.route("/download", methods= ["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host='0.0.0.0', port=8080, debug=True)

