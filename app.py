from flask import Flask, request, jsonify
import json
from waitress import serve
from datetime import timedelta

import os
from minio import Minio
from minio.error import ResponseError


app = Flask(__name__)

PORT = 8080

minioClient = Minio("minio-test.cap.jaagalabs.com",
                    access_key='jaaga',
                    secret_key='1jaagaLove',
                    secure=True)
bucket_name = "test"


@app.route("/")
def entry():
    return "working"


@app.route("/create_presigned_url", methods=['POST'])
def presign_url():

    req = request.json
    file_name = req["file_name"]
    presigned_url = ""

    try:

        presigned_url = minioClient.presigned_put_object(bucket_name,
                                                         file_name,
                                                         expires=timedelta(days=3))
    except ResponseError as err:
        print(err)

    result = {
        "status": "worked",
        "presigned_url": presigned_url
    }

    return jsonify(result)


if __name__ == "__main__":
    # app.run(debug=True)
    serve(app, listen='*:{}'.format(str(PORT)))
