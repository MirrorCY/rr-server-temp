from flask import Flask, request, send_from_directory
import os
import threading
import time
import logging


MAX_UPLOAD_SIZE_MB = 10
UPLOAD_FOLDER = "uploads"
IP_ADDRESS = "42.193.147.60"
PORT = 4244
READ_FILE_TIMEOUT = 60
HEAD_FILE_TIMEOUT = 4
DEFAULT_FILE = "404.png"

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/portal/push", methods=["POST"])
def push_something():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]

    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        logging.info(f"Saving file: {filename}")
        file.save(filepath)
        threading.Thread(target=delete_file, args=(filepath,)).start()
        return f"http://{IP_ADDRESS}:{PORT}/portal/pull/{filename}"

# 似乎只有 md 消息才 HEAD，这里用来拖超时时间，但没资格没法测试
# @app.route("/portal/pull/<filename>", methods=["HEAD"])
# def head_something(filename):
#     if filename:
#         start_time = time.time()
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         while not os.path.exists(filepath):
#             time.sleep(0.05)
#             if time.time() - start_time > HEAD_FILE_TIMEOUT:
#                 logging.info(f"File {filename} not found, HEAD request timed out")
#                 break
#         return 200
#     else:
#         return "File parameter is missing", 400


@app.route("/portal/pull/<filename>", methods=["GET"])
def pull_something(filename):
    if filename:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        start_time = time.time()
        while not os.path.exists(filepath):
            time.sleep(0.05)
            if time.time() - start_time > READ_FILE_TIMEOUT:
                logging.info(f"File {filename} not found, serving default 404")
                return send_from_directory("./", DEFAULT_FILE, as_attachment=True)

        logging.info(f"Serving file: {filename}")
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    else:
        return "File parameter is missing", 400


def delete_file(filepath):
    time.sleep(60)
    os.remove(filepath)
    logging.info(f"Deleted file: {os.path.basename(filepath)}")


if __name__ == "__main__":
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
            logging.info(f"Deleted file: {filename}")

    app.run(host="0.0.0.0", port=PORT)
