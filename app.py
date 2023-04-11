import os

from flask import Flask, redirect, render_template, url_for, request, session, jsonify, json, flash
from werkzeug.utils import secure_filename

import face_verification

import dataset
import preprocess


app = Flask(__name__)

# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


# def formatName(user_id="", time="", ):
#     return user_id + '_' + datetime.strptime(time, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d-%H-%M-%S')


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


URL = "http://103.121.91.247/ImageCPC1HN"
UPLOAD_FOLDER = 'temp'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.secret_key = "secret key"

sample = {
    "token": "",
    "UserId": "",
    "UploadImg": [{
        "URL": "http://103.121.91.247/ImageCPC1HN/File/Download?UserName=checkimage&UserId=0356116111&CallId=9622cd2b-e8c6-485e-9c1c-7c071975ce4d&FileName=3&Token=23C75BD161BD449E9CD4CFE72BC71470",
        "UploadTime": "2022-05-04 15:45:18"
        # "name": "",
    }]
}

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

rfa = dataset.RoboflowController(project_name="2yeardataset",
                                 api_key="mfrbcbsvA7OvqaeeQHac",
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

        # example_id = "0356116111"

        userID = request.form["userid"]
        dts = dataset.Uniform(url=URL,username="checkimage",pwd="123")

        sample_image = face_verification.downloadSample(userID,dts,max_images=3,save_dir=UPLOAD_FOLDER)
        print(sample_image)

        for img in sample_image:
            preprocess.autorotate(img)



        # Preprocessing
        # if not request['isProcessed']:

        result_response = {
            "face": True,
            "predict": None
        }

        for img in all_images:
            preprocess.autorotate(img)
            if not face_verification.deepface(img,sample_image):
                result_response["face"] = False
                return result_response

            preprocess.autoresize(img, 640, 640)


        # preprocess.process_directory(UPLOAD_FOLDER,recursive=True)
        result_response["predict"] = rfa.predict(8, files=all_images)

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
