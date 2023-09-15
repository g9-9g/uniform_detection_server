import functools
import numpy as np
from PIL import Image
import asyncio

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

bp = Blueprint('predict', __name__, url_prefix='/predict')

from src.utils.api import handle_files, handle_err, empty_folder
from src.utils.preprocess import *
from src.utils.face_verification import *
from src.routes.auth import login_required
from src.utils.dataset import *

@bp.route('/', methods=['GET', 'POST'])
# @login_required
def predict():
    if request.method == 'GET':
        return render_template('predict/insert.html')

    # userIDs,images = handle_files(request, current_app.config['UPLOAD_FOLDER'])
    # print(userIDs,images)
    print(request.files)
    uploaded_files = request.files
    response_result = {} 
    # for field_name, file in uploaded_files.items():
    #         if file.filename == '':
    #             continue  # Skip empty file fields

    #         # Save the file to the upload directory
    #         file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
    # for userID in userIDs:
    #     response_result[userID] = {'face' : None, 'uniform' : None}

    # try:
        
    #     sample_embeddings = {}

    #     # Get local embeddings, if not exist, download it from server
    #     for userID in userIDs:
    #         known_embedding = load_sample(user_id=userID,save_dir=current_app.config['DATASET_FOLDER'])
    #         sample_embeddings[userID] = known_embedding

    #     process_images(images)

    #     # Filter out images with no face detected
    #     unknown_aligned = detect_faces(images)   
    #     unknown_embeddings = get_embeddings(unknown_aligned)

    #     # Face verification
    #     threshold = current_app.config['COSINE_SIMILARITY_THRESHOLD']
    #     for i, userID in enumerate(userIDs):
    #         unknown_embedding = unknown_embeddings[i]
    #         sample_embedding = sample_embeddings[userID]
    #         if unknown_embedding is None or sample_embedding is None: 
    #             continue
            
    #         avg_dist = np.mean([distance(unknown_embedding, se, distance_metric=1) for se in sample_embedding])
    #         print("avg_distance = ", avg_dist)
    #         response_result[userID]= {"face": str(avg_dist < threshold), "uniform" : None}


    #     # Uniform detection
    #     class_names = {
    #         0: "ao",
    #         1: "balo",
    #         2: "mu"
    #     }
    #     results = current_app.config.model(images)
    #     for userID, result in zip(userIDs, results):
    #         prediction = result.boxes.cpu().numpy()
    #         cl = prediction.cls.copy()
    #         conf = prediction.conf.copy().astype('str')
    #         response_result[userID]['uniform']=[(class_names[i], j) for i, j in zip(cl, conf)]
        
    #     session['result'] = response_result
    #     print(response_result)
    # except Exception as e:
    #     handle_err(e)

    return response_result



@bp.route('/download_sample', methods=['POST']) 
@login_required
def ds():
    uids = request.form.get('uids')
    max_images = request.form.get('max_images')
    filters = request.form.get('filters')
    response_result = {}
    try:
        if uids is None:
            raise Exception("Error no uids")
        if max_images is None:
            max_images = 5
        for uid in uids:
            embeddings = download_sample(uid, max_images, current_app.config['DATASET_FOLDER'])
            if embeddings is not None:
                response_result[uid].status = 'OK'
            else:
                response_result[uid].status = 'USER NOT EXIST'
            
    except Exception as e:
        response_result['error'] = e

    return response_result

@bp.after_request
def after_request_callback(response):
    # empty_folder(current_app.config['UPLOAD_FOLDER'])
    return response

@bp.route('/result', methods=['POST', 'GET'])
async def get_result():
    return render_template('predict/insert.html')