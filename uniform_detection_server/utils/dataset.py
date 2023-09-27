import requests
from datetime import datetime
from PIL import Image
import os

from . import face_verification
from . import preprocess
import numpy as np
from flask import session


def connect_db(username, password):
    token = requests.post('http://103.121.91.247/ImageCPC1HN/User/UserLogin', data={'UserName': username, 'Password': password}).json()['Token']
    if token:
        session['username'] = username
        session['token'] = token
    else:
        raise Exception("Incorrect password or username")
    
    return token

def close_db():
    if 'username' in session:
        session.pop('username')
    if 'token' in session:
        session.pop('token')

def get_user_list():
    if session['token']:
        return requests.post('http://103.121.91.247/ImageCPC1HN/User/Get_userLst', data={
            'UserName': session['username'],
            'Token': session['token']
        }).json()["UserLst"]
    return None

def get_image_per_user(user_id, TIME_START="2020-05-05",TIME_END=datetime.today().strftime("%Y-%m-%d")):
    res = requests.post('http://103.121.91.247/ImageCPC1HN/Call/GetImageLstByUser', data={
        'UserName': session['username'],
        'Token': session['token'],
        'UserId': user_id,
        'TimeStart': TIME_START,
        'TimeEnd': TIME_END,
    })
    return [obj['LinkImage'] for obj in res.json()['LinkImageLst']]


def download_sample(user_id, max_images=5,save_dir='temp', random=False, saved=True):
    if os.path.exists(os.path.join(save_dir, user_id + ".npy")):       
        return np.load(os.path.join(save_dir, user_id + ".npy"))
    all_images = get_image_per_user(user_id)
    # known_images = []
    known_embeddings = []
    known_aligned = []
    cnt = 0
    for url in all_images:
        if (cnt >= int(max_images)):
            break
        
        response = requests.get(url,  stream=True)
        image = Image.open(response.raw)
        image = preprocess.remove_alpha_channel(preprocess.autoresize(preprocess.autorotate(image)))
        aligned =  face_verification.detect_face(image)
        if aligned is not None:
            known_aligned.append(aligned)
            cnt+=1

    if not known_aligned:
        return None
    
    known_embeddings = face_verification.calculate_embeddings(known_aligned)
    if saved:
        print("SAVED")
        np.save(os.path.join(save_dir, user_id + ".npy"), known_embeddings)  

    return known_embeddings

def load_sample (user_id, save_dir='temp'):
    if os.path.exists(os.path.join(save_dir, user_id + ".npy")):       
        return np.load(os.path.join(save_dir, user_id + ".npy"))
    else:
        return None