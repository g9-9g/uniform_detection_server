import os

from flask import Flask, redirect, render_template, url_for, request, session, jsonify, json, flash
from werkzeug.utils import secure_filename

import face_verification

import dataset
import preprocess
import uniform_detection


from constant import *

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.secret_key = SECRET_KEY



rfa = uniform_detection.RoboflowController(project_name=PROJECT_NAME,
                                 api_key=API_KEY,
                                 env="Dataset")


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

        try:
            userID = request.form["userid"]
            dts = dataset.Uniform(url=URL,username=ADMIN["username"],pwd=ADMIN["pwd"])

            sample_image = face_verification.downloadSample(userID,dts,max_images=3,save_dir=UPLOAD_FOLDER)
            
            if not sample_image:
                raise Exception("NO SAMPLE IMAGE OF USER: ", userID)
        except Exception as e:
            print(e)
        
        # Initial response
        result_response = {
            "face": True,
            "predict": None,
            "error" : None
        }

        preprocess.multirotate(sample_image)

        # Face verification
        for img in all_images:
            preprocess.autorotate(img)
            if not face_verification.deepface(img, sample_image):
                result_response["face"] = False
                return result_response

            preprocess.autoresize(img, 640, 640)

        # Uniform detection
        try:
            result_response["predict"] = rfa.predict(8, files=all_images)
        except Exception as err:
            print(err)
            result_response["error"] = err
        # save result
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
    app.run()
