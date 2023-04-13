import io
import os

import requests
from PIL import Image
from deepface import DeepFace
from datetime import datetime

TIME_START = "2020-10-01"
TIME_END = datetime.today().strftime("%Y-%m-%d")

def downloadSample(user_id, dataset, max_images,save_dir, time=(TIME_START, TIME_END), random=False):
    if not save_dir:
        raise Exception("No output folder")

    all_images = dataset.getImagePerUser(user_id, time)
    known_images = []
    cnt = 0
    for image in all_images:
        if cnt >= max_images:
            break
        try:
            response = requests.get(image, allow_redirects=True)
            img = Image.open(io.BytesIO(response.content))
            img.save(os.path.join(save_dir, 'a{}.jpg'.format(cnt)))
            img.close()
        finally:
            known_images.append(os.path.join(save_dir, 'a{}.jpg'.format(cnt)))
            cnt += 1

    return known_images

def deepface(unknown_image, known_images):
    try:
        if known_images: 
            mean_distance = 0
            for img in known_images:
                res = DeepFace.verify(img1_path=unknown_image,
                                    img2_path=img, model_name='Facenet512', distance_metric='euclidean_l2',
                                    detector_backend='retinaface')
                mean_distance += res['distance']

            mean_distance /= len(known_images)


            return mean_distance < 1.04
        else: 
            return 0
    except:
        return 0
