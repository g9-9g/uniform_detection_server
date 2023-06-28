import os
import argparse

from flask import Flask, redirect, render_template, url_for, request, session, jsonify, json, flash,make_response
from werkzeug.utils import secure_filename

import api
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        try:
            token = dataset.Uniform(username).get_token(pwd)
            if token:
                session['token'] = token
                session['username'] = username
                print(token, username)
                return redirect(url_for('predict'))
        except Exception as e:
            pass
    print("AUTH ERROR")
    return LOGIN_FORM

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('token', None)
    session.pop('result',None)
    return redirect(url_for('login'))


@app.route("/", methods=['POST', 'GET'])
def predict():
    if request.method == 'GET':
        if 'token' not in session or 'username' not in session:
            return redirect(url_for('login'))
        return render_template('upload.html')
    
    token, username = session['token'] ,session['username']
    userIDs , images = api.handle_files(request)
    print(userIDs,images)
    response_result = {}
    for userID in userIDs:
        response_result[userID] = {'face' : None, 'uniform' : None}

    try:
        data = dataset.Uniform(username,token)
        # if not data.check_token():
        #     print("Token expired")
        #     return redirect(url_for('login'))
        
        sample_embeddings = {}

        # Get local embeddings, if not exist, download it from server
        for userID in userIDs:
            known_embedding = data.download_sample(userID,5)
            sample_embeddings[userID] = known_embedding


        preprocess.process_images(images)

        # Filter out images with no face detected
        
        unknown_aligned = face_verification.detect_faces(images)   
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
            response_result[userID]= {"face": str(np.less(avg_dist, threshold)), "uniform" : None}


        # Uniform detection
        class_names = {
            0: "ao",
            1: "balo",
            2: "mu"
        }
        results = model(images)
        for userID, result in zip(userIDs, results):
            prediction = result.boxes.cpu().numpy()
            cl = prediction.cls.copy()
            conf = prediction.conf.copy().astype('str')
            response_result[userID]['uniform']=[(class_names[i], j) for i, j in zip(cl, conf)]

    except Exception as e:
        api.handle_err(e)

    print(response_result)
    session['result'] = response_result

    return redirect('/save_result')


@app.route("/save_result", methods=['GET'])
def save_result():
    if 'token' not in session or 'username' not in session:
        return redirect(url_for('login'))
    result = session['result']
    if not result:
        return "No updated found"

    return result


@app.after_request
def after_request_callback(response):
    if request.path == '/':
        api.empty_folder(UPLOAD_FOLDER)

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
