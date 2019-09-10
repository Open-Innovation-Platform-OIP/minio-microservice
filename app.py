from flask import Flask, request, jsonify
import json
from waitress import serve
from datetime import timedelta

import os
from minio import Minio
from minio.error import ResponseError


app = Flask(__name__)

PORT = 8080

minioClient = Minio("https://minio-test.cap.jaagalabs.com",
                    access_key='jaaga',
                    secret_key='1jaagaLove',
                    secure=True)
bucket_name = "test"


@app.route("/create_presign_url", methods=['GET'])
def presign_url():

    trigger_payload = request.json
    presigned_url = ""

    try:

        presigned_url = minioClient.presigned_put_object(bucket_name,
                                                         'video',
                                                         expires=timedelta(days=3))
    except ResponseError as err:
        print(err)

    return presigned_url


if __name__ == "__main__":
    # app.run(debug=True)
    serve(app, listen='*:{}'.format(str(PORT)))
