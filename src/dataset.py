import requests
from datetime import datetime
from constant import *

import face_verification
import preprocess
import numpy as np


class Uniform:
    ADMIN = {}
    users = {}
    token = None
    filters = []

    def __init__(self, url, username, pwd=None, token=None):
        self.URL = url
        self.TIME_START = DEFAULT_STARTTIME
        self.TIME_END = datetime.today().strftime("%Y-%m-%d")
        if token:
            self.token = token
            return
        self.ADMIN = {
            "userName": username,
            "Password": pwd
        }
        if not self.token:
            self.get_token()

    def get_token(self):
        if not self.ADMIN:
            raise Exception("Auth error")
        self.token = requests.post('{}/User/UserLogin'.format(self.URL), data=self.ADMIN).json()['Token']
        return self.token

    def get_user(self):
        if not self.token:
            self.get_token()
        if not self.users:
            self.users = requests.post('{}/User/Get_userLst'.format(self.URL), data={
                'UserName': self.ADMIN['userName'],
                'Token': self.token
            }).json()["UserLst"]
        return self.users

    def get_image_per_user(self, user_id, time=None):
        if not time:
            time = (self.TIME_START, self.TIME_END)
        res = requests.post('{}/Call/GetImageLstByUser'.format(self.URL), data={
            'UserName': self.ADMIN["userName"],
            'Token': self.token,
            'UserId': user_id,
            'TimeStart': time[0],
            'TimeEnd': time[1],
        })
        return [obj['LinkImage'] for obj in res.json()['LinkImageLst']]

    # def filter(self, time, max_level, take_high_level_employee):
    #     if not self.users:
    #         self.get_user()

    #     results = []

    #     for user in self.users:
    #         userid = user['UserId']
    #         if take_high_level_employee and (user['EmployeeLevel'] < max_level):
    #             continue
    #         data = self.get_image_per_user(time, userid)["LinkImageLst"]

    #         for data_img in data:
    #             img_name = formatName(userid, data_img['TimeImage'])
    #             results.append({"name": img_name, "url": data_img['LinkImage']})

    def download_sample(self, user_id, max_images=5,save_dir=DATASET_FOLDER, random=False, saved=True):        
        if os.path.exists(os.path.join(save_dir, user_id + ".npy")):
            return np.load(os.path.join(save_dir, user_id + ".npy"))
    
        all_images = self.get_image_per_user(user_id)
        # known_images = []
        known_embeddings = []
        known_aligned = []
        cnt = 0
        for url in all_images:
            if (cnt >= max_images):
                break
            response = requests.get(url, allow_redirects=True)
            dir = os.path.join(UPLOAD_FOLDER, '{}_{}.jpg'.format(user_id, cnt))
            with open(dir, 'wb') as f:
                f.write(response.content)
            preprocess.process_images([dir])
            aligned =  face_verification.detect_faces([dir])
            if aligned:
                known_aligned.append(aligned[0])
                cnt+=1
            
        if not known_aligned:
            return None
        
        known_embeddings = face_verification.calculate_embeddings(known_aligned)

        if saved:
            np.save(os.path.join(save_dir, user_id + ".npy"), known_embeddings)  

        return known_embeddings
