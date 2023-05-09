import os
import argparse

from flask import Flask, redirect, render_template, url_for, request, session, jsonify, json, flash
from werkzeug.utils import secure_filename

import face_verification
import dataset
import preprocess
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
        except Exception as e:
            print(e)

        dts = dataset.Uniform(url=URL,username=ADMIN["username"],pwd=ADMIN["pwd"])
        sample_embeddings = []
        filtered_userIDs = []
        filtered_images = []
        for (userID, image) in zip(userIDs, all_images):
            sample_img = dts.downloadSample(userID, max_images=1,save_dir=UPLOAD_FOLDER)
            preprocess.multirotate(sample_img)
            preprocess.multiresize(sample_img)
            known_aligned = face_verification.detect_faces(sample_img)
            known_aligned = list(filter(lambda item: item is not None, known_aligned))
            if not known_aligned: 
                result_response[userID] = {'face': False, 'uniform': None}
                # raise Exception("NO FACE DETECTED IN SAMPLE IMAGES OF USER: ", userID)
                print("NO FACE DETECTED IN SAMPLE IMAGES OF USER: ", userID)
            else:
                known_embeddings = face_verification.calculate_embeddings(known_aligned)
                sample_embeddings.append(known_embeddings)
                filtered_userIDs.append(userID)
                filtered_images.append(image)
        
        # Preprocess
        preprocess.multirotate(filtered_images)
        preprocess.multiresize(filtered_images)

        # Filter out images with no face detected
        unknown_aligned = face_verification.detect_faces(filtered_images)
        filtered_filtered_userIDs = []
        filtered_unknown_aligned = []
        filtered_sample_embeddings = []
        filtered_filtered_images = []

        for (userID, align, se, img) in zip(filtered_userIDs, unknown_aligned, sample_embeddings, filtered_images):
            if align is None:
                result_response[userID] = {'face': False, 'uniform': None}
                print("NO FACE DETECTED IN IMAGE OF USER: ", userID)
            else:
                filtered_filtered_userIDs.append(userID)
                filtered_unknown_aligned.append(align)
                filtered_sample_embeddings.append(se)
                filtered_filtered_images.append(img)

        filtered_userIDs = filtered_filtered_userIDs
        filtered_images = filtered_filtered_images
        sample_embeddings = filtered_sample_embeddings
        unknown_embeddings = face_verification.calculate_embeddings(filtered_unknown_aligned)  

        # Uniform detection
        results = model(filtered_images)
        # print(results)
        # print(results.probs)  # cls prob, (num_class, )


        # threshold = 0.71

        # # Face verification
        # for (userID, unknown_embedding, sample_embedding) in zip(filtered_userIDs, unknown_embeddings, sample_embeddings):
        #     avg_dist = sum([(unknown_embedding - se).norm().item() for se in sample_embedding])/len(sample_embedding)
        #     print("distance = ", avg_dist)
            
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
