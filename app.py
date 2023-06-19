import os
import argparse

from flask import Flask, redirect, render_template, url_for, request, session, jsonify, json, flash
from werkzeug.utils import secure_filename

import face_verification
import dataset
import preprocess
import numpy as np
from ultralytics import YOLO

from constant import *

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.secret_key = SECRET_KEY



# rfa = uniform_detection.RoboflowController(project_name=PROJECT_NAME,
#                                  api_key=API_KEY,
#                                  env="Dataset")


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
        # result of each user should include user_id, face, uniform

        # Sample Image
        try:
            userIDs = request.form['textlist'].split(' ')
            if len(userIDs) != len(all_images):
                raise Exception("Number of images and userIDs are not equal")
            dts = dataset.Uniform(url=URL,username=ADMIN["username"],pwd=ADMIN["pwd"])
            test_data = dict(zip(userIDs, all_images))
            sample_embeddings = {}

            for userID in userIDs:
                if not os.path.exists(os.path.join(DATASET_FOLDER, userID + ".npy")):
                    sample_img = dts.downloadSample(userID, max_images=5,save_dir=UPLOAD_FOLDER)
                    preprocess.process_images(sample_img)
                    known_aligned = face_verification.detect_faces(sample_img)
                    known_aligned = list(filter(lambda item: item is not None, known_aligned))
                    if not known_aligned: 
                        result_response[userID] = {'face': False, 'uniform': None}
                        print("NO FACE DETECTED IN SAMPLE IMAGES OF USER: ", userID)
                        del test_data[userID]
                    else:
                        known_embeddings = face_verification.calculate_embeddings(known_aligned)
                        sample_embeddings[userID] = known_embeddings
                        np.save(os.path.join(DATASET_FOLDER, userID + ".npy"), known_embeddings)
                else:
                    sample_embeddings[userID] = np.load(os.path.join(DATASET_FOLDER, userID + ".npy"))

            # Preprocess
            if not test_data:
                raise Exception("NO FACE DETECTED IN SAMPLE IMAGES OF ALL USERS")
            
            filtered_images = list(test_data.values())
            preprocess.process_images(filtered_images)

            # Filter out images with no face detected
            unknown_aligned = face_verification.detect_faces(filtered_images)
            filtered_aligned = []
            userIDs = list(test_data.keys()).copy()
            for (userID, align) in zip(userIDs, unknown_aligned):
                if align is None:
                    result_response[userID] = {'face': False, 'uniform': None}
                    print("NO FACE DETECTED IN IMAGE OF USER: ", userID)
                    del test_data[userID]
                    del sample_embeddings[userID]   
                else:
                    filtered_aligned.append(align)

            if not test_data:
                raise Exception("NO FACE DETECTED IN TEST IMAGES OF ALL USERS")
            
            unknown_embeddings = face_verification.get_embeddings(filtered_aligned)
            userIDs = test_data.keys()
            filtered_images = list(test_data.values())

            # Face verification
            threshold = COSINE_SIMILARITY_THRESHOLD
            for i, userID in enumerate(userIDs):
                unknown_embedding = unknown_embeddings[i]
                # test_data[userID] = unknown_embedding
                sample_embedding = sample_embeddings[userID]
                
                avg_dist = np.mean([face_verification.distance(unknown_embedding, se, distance_metric=1) for se in sample_embedding])
                print("avg_distance = ", avg_dist)
                if avg_dist > threshold:
                    result_response[userID] = {'face': False, 'uniform': None}
                else:
                    result_response[userID] = {'face': True, 'uniform': None}

            # Uniform detection
            class_names = {
                0: "ao",
                1: "balo",
                2: "mu"
            }
            results = model(filtered_images)
            for result in results:
                prediction = result.boxes.cpu().numpy()
                cl = prediction.cls.copy()
                result_response[userID]['uniform'] = [class_names[i] for i in cl]

        except Exception as e:
            print(e)

        print(result_response)
        session['result'] = result_response

        redirect('/')
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
        # Do something after the request has been processed

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
    model = YOLO("best.pt")
    app.run(host="127.0.0.1", port=args.port)
