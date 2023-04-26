import io
import os

import requests
from PIL import Image
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


