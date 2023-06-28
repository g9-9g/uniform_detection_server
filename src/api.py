from werkzeug.utils import secure_filename
from constant import *
import os

import json 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_files (request):
    if 'files[]' not in request.files:
        raise Exception("No file part")

    files = request.files.getlist('files[]')
    userIDs = request.form['textlist'].split(' ')

    if len(userIDs) != len(files):
        raise Exception("Number of images and userIDs are not equal")
    
    data = []

    for file, userID in zip(files, userIDs):
        userID = str(userID)
        if file and allowed_file(file.filename) and userID.isnumeric():
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            data.append((userID, os.path.join(UPLOAD_FOLDER, filename)))

    return ([d[0] for d in data], [d[1] for d in data])


def empty_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path} - {e}")


def handle_err (e):
    print(e)