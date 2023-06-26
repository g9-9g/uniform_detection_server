import os
import argparse

from flask import Flask, redirect, render_template, url_for, request, session, jsonify, json, flash
from werkzeug.utils import secure_filename

import face_verification
import dataset
import preprocess
from ultralytics import YOLO
from constant import *

import numpy as np

app = Flask(__name__, template_folder='../templates')


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.secret_key = SECRET_KEY


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route("/", methods=['POST'])
def predict():
    if request.method == 'POST':
        # Download
        if 'files[]' not in request.files:
            flash('No file part')

        files = request.files.getlist('files[]')
        all_images = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                all_images.append(os.path.join(UPLOAD_FOLDER, filename))

        flash('File(s) successfully uploaded')
        
        # Initial response
        result_response = {}

        # Sample Image
        try:
            userIDs = request.form['textlist'].split(' ')
            if len(userIDs) != len(all_images):
                raise Exception("Number of images and userIDs are not equal")
                
            dts = dataset.Uniform(url=URL,username=ADMIN["username"],pwd=ADMIN["pwd"])
            sample_embeddings = {}

            for userID in userIDs:
                known_embedding = dts.download_sample(userID,5)
                sample_embeddings[userID] = known_embedding

                # Set default result value
                result_response[userID] = {'face': None, 'uniform': None}
                

            # Preprocess
            preprocess.process_images(all_images)

            # Filter out images with no face detected
            
            unknown_aligned = face_verification.detect_faces(all_images)   
            unknown_embeddings = face_verification.get_embeddings(unknown_aligned)

            # Face verification
            threshold = COSINE_SIMILARITY_THRESHOLD
            for i, userID in enumerate(userIDs):
                unknown_embedding = unknown_embeddings[i]
                sample_embedding = sample_embeddings[userID]
                if unknown_embedding is None or sample_embedding is None: 
                    continue
                
                avg_dist = np.mean([face_verification.distance(unknown_embedding, se, distance_metric=1) for se in sample_embedding])
                print("avg_distance = ", avg_dist)
                result_response[userID] = {'face':  str(avg_dist < threshold), 'uniform': None}
                    

            # Uniform detection
            class_names = {
                0: "ao",
                1: "balo",
                2: "mu"
            }
            results = model(all_images)
            for result in results:
                prediction = result.boxes.cpu().numpy()
                cl = prediction.cls.copy()
                conf = prediction.conf.copy().astype('str')
                result_response[userID]['uniform'] = [(class_names[i], j) for i, j in zip(cl, conf)]

        except Exception as e:
            print(e)

        print(result_response)
        session['result'] = result_response

        # redirect('/')
        return result_response


@app.route("/save_result", methods=['GET'])
def save_result():
    result = session['result']
    if not result:
        return "No updated found"

    return result

@app.after_request
def after_request_callback(response):
    if request.path == '/':
        # Empty upload folder
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {file_path} - {e}")
        pass
        #

    return response

# always run when build (for debugging)
with app.test_request_context():
    print("hello")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Flask app exposing yolov8 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()
    model = YOLO("models\\best.pt")
    app.run(host="127.0.0.1", port=args.port)
