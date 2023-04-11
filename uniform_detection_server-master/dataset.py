import requests
from datetime import datetime


class Uniform:
    ADMIN = {}
    users = {}
    token = None
    filters = []

    def __init__(self, url, username, pwd=None, token=None):
        self.URL = url
        self.TIME_START = "2020-10-01"
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

    def filter(self, time, max_level, ):
        if not self.users:
            self.getUser()

        results = []

        for user in self.users:
            userid = user['UserId']
            # if user['EmployeeLevel'] < max_level:
            #     continue
            data = self.getImagePerUser(time, userid)["LinkImageLst"]

            for data_img in data:
                img_name = formatName(userid, data_img['TimeImage'])
                results.append({"name": img_name, "url": data_img['LinkImage']})


if __name__ == '__main__':
    unf = Uniform("http://103.121.91.247/ImageCPC1HN", username="checkimage",pwd="123")
