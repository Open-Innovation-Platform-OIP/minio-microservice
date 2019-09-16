from flask import Flask, request, jsonify
import json
from waitress import serve
from datetime import timedelta
import os
from minio import Minio
from minio.error import ResponseError
from flask_cors import CORS
import jwt


app = Flask(__name__)
CORS(app)


PORT = 8080


minioClient = Minio(os.environ['MINIO_HTTPS_ENDPOINT'], access_key=os.environ['MINIO_ACCESS_KEY'],
                    secret_key=os.environ['MINIO_SECRET_KEY'], secure=True)


@app.route("/create_presigned_url", methods=['POST'])
def presign_url():

    req = request.json
    file_data = req["file_data"].split("/")
    jwt_token = req.headers["authorization"]
    # return jwt_token

    try:

        is_authorized = jwt.decode(jwt_token, os.environ['ENCRYPTION_KEY'],
                                   algorithms=['HS256'])
    except:
        result = {"error": "User not authorized to upload file"}
        result = jsonify(result)
        result.status_code = 400

        return result

    bucket_name = file_data[0]
    file_name = file_data[1]
    presigned_url = ""

    try:

        presigned_url = minioClient.presigned_put_object(bucket_name,
                                                         file_name,
                                                         expires=timedelta(days=3))
    except ResponseError as err:
        print(err)

    if presigned_url:

        result = {
            "status": "Success",
            "presigned_url": presigned_url
        }
        result = jsonify(result)
        result.status_code = 200
    else:
        result = {
            "error": "Could not generate a url"
        }
        result = jsonify(result)
        result.status_code = 404

    return result


@app.route("/get_url", methods=['POST'])
def get_presigned_url():
    req = request.json
    file_data = req["file_data"].split("/")
    bucket_name = file_data[0]
    file_name = file_data[1]
    url = ""

    try:

        url = minioClient.presigned_get_object(
            bucket_name, file_name, expires=timedelta(days=2))
# # Response error is still possible since internally presigned does get bucket location.
    except ResponseError as err:

        print(err)

    if url:

        result = {
            "status": "Success",
            "url": url
        }
        result = jsonify(result)
        result.status_code = 200
    else:
        result = {
            "status": "Error,could not generate a url"
        }
        result = jsonify(result)
        result.status_code = 404

    return result


if __name__ == "__main__":
    # app.run(debug=True)
    serve(app, listen='*:{}'.format(str(PORT)))
