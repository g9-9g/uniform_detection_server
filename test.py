import requests
url = "http://127.0.0.1:5000/predict"

multiple_files = [('12', ('1.jpg', open('tests\\1.jpg', 'rb'), 'image/jpg')),
                      ('34', ('2.jpg', open('tests\\2.jpg', 'rb'), 'image/jpg')),
                      ('34', ('3.jpg', open('tests\\3.jpg', 'rb'), 'image/jpg'))]

data={'uids': ['12','34','5']}
r = requests.post(url, files=multiple_files,data=data)
print(r.text)