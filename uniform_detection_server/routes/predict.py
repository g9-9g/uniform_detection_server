import functools
import numpy as np
from PIL import Image

from flask_cors import CORS

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

bp = Blueprint('predict', __name__, url_prefix='/predict')

from uniform_detection_server.utils.api import handle_files, handle_err, empty_folder
from uniform_detection_server.utils.preprocess import *
from uniform_detection_server.utils.face_verification import *
from uniform_detection_server.routes.auth import login_required
from uniform_detection_server.utils.dataset import *

@bp.route('/', methods=['GET', 'POST'])
@login_required
# @cross_origin()
def predict():
    if request.method == 'GET':
        return render_template('predict/insert.html')

    image_paths, userIDs = handle_files(request, current_app.config.tempfolder)
    response_result = {} 
    error = []

    threshold = current_app.config['COSINE_SIMILARITY_THRESHOLD']
    sample_embeddings = {}
    unknown_embeddings = {}

    # Get local embeddings, if not exist, download it from server
    for userID in userIDs:
        known_embedding = load_sample(user_id=userID,save_dir=current_app.config['DATASET_FOLDER'])
        sample_embeddings[userID] = known_embedding

    # Face Vertification
    for userID in userIDs:
        if not userID in image_paths:
            error.append(f'No image of user{userID}')
            continue

        if sample_embeddings[userID] is None:
            error.append(f'user{userID} have no sample_embeddings')
            continue
    
        response_result[userID] = {'result' : []}
        unknown_embeddings[userID] = []

        for img in image_paths[userID]:
            process_images([img])
            try:      
                unknown_aligned = detect_faces([img])
                unknown_embeddings[userID].append(get_embeddings(unknown_aligned)[0])
            except Exception as e:
                error.append(f'Cannot detect face in image{img}')
                continue

        for unknown_embedding in unknown_embeddings[userID]:
            avg_dist = np.mean([distance(unknown_embedding, se, distance_metric=1) for se in sample_embeddings[userID]])
            print("avg_distance = ", avg_dist)
            response_result[userID]['result'].append({"face": str(avg_dist < threshold)})


    # Uniform detection
    class_names = {
        0: "ao",
        1: "balo",
        2: "mu"
    }
    # print(userIDs, response_result)
    for userID in userIDs:
        if userID in image_paths and not sample_embeddings[userID] is None and userID in unknown_embeddings:
            for index, image in enumerate(image_paths[userID]):
                try:
                    result = current_app.config.model(image)[0]
                    prediction = result.boxes.cpu().numpy()
                    cl = prediction.cls.copy()
                    conf = prediction.conf.copy().astype('str')
                    response_result[userID]['result'][index]['uniform'] = ([(class_names[i], j) for i, j in zip(cl, conf)])
                except Exception as e:
                    error.append(f'error {e} at image{index} of user{userID}')

    print(response_result)
    response_result["errors": error]

    return response_result



@bp.route('/download_sample', methods=['POST']) 
@login_required
def ds():
    uids = request.form.getlist('uids')
    max_images = request.form.get('max_images')
    # filters = request.form.get('filters')
    response_result = {}
    try:
        if uids is None:
            raise Exception("Error no uids")
        
        if max_images is None:
            max_images = 5
        for uid in uids:
            embeddings = download_sample(uid, max_images, current_app.config['DATASET_FOLDER'])
            if embeddings is not None:
                response_result[uid] = {'status' : 'OK'}
            else:
                response_result[uid] = {'status' : 'User not exist'}
            
    except Exception as e:
        print(e)
        response_result['error'] = "Server not respond"

    return response_result

@bp.after_request
def after_request_callback(response):
    empty_folder(current_app.config.tempfolder)
    return response

@bp.route('/result', methods=['POST', 'GET'])
async def get_result():
    return render_template('predict/insert.html')