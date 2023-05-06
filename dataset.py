import requests
from datetime import datetime
from constant import *
from PIL import Image
import io
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
            self.getToken()

    def getToken(self):
        if not self.ADMIN:
            raise Exception("Auth error")
        self.token = requests.post('{}/User/UserLogin'.format(self.URL), data=self.ADMIN).json()['Token']
        return self.token

    def getUser(self):
        if not self.token:
            self.getToken()
        if not self.users:
            self.users = requests.post('{}/User/GetUserLst'.format(self.URL), data={
                'UserName': self.ADMIN['userName'],
                'Token': self.token
            }).json()["UserLst"]
        return self.users

    def getImagePerUser(self, user_id, time=None):
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
    #         self.getUser()

    #     results = []

    #     for user in self.users:
    #         userid = user['UserId']
    #         if take_high_level_employee and (user['EmployeeLevel'] < max_level):
    #             continue
    #         data = self.getImagePerUser(time, userid)["LinkImageLst"]

    #         for data_img in data:
    #             img_name = formatName(userid, data_img['TimeImage'])
    #             results.append({"name": img_name, "url": data_img['LinkImage']})

    def downloadSample(self, user_id, max_images,save_dir, random=False):
        if not save_dir:
            raise Exception("No output folder")

        all_images = self.getImagePerUser(user_id)
        known_images = []
        cnt = 0
        for image in all_images:
            if cnt >= max_images:
                break
            try:
                response = requests.get(image, allow_redirects=True)
                with open(os.path.join(save_dir, '{}_{}.jpg'.format(user_id, cnt)), 'wb') as f:
                    f.write(response.content)
            finally:
                known_images.append(os.path.join(save_dir, '{}_{}.jpg'.format(user_id, cnt)))
                cnt += 1

        return known_images


if __name__ == '__main__':
    unf = Uniform(URL, username="checkimage",pwd="123")
