import requests
url = "http://127.0.0.1:5000/auth/login"

session = requests.Session()

data={'username': "checkimage",
      'password': "123",
      "remember": True}

r = session.post(url,data=data)
print(r.text)

multiple_files = [('0325933434', ('1.jpg', open('images\\1.jpg', 'rb'), 'image/jpg')),
                      ('34', ('2.jpg', open('images\\2.jpg', 'rb'), 'image/jpg')),
                      ('0325933434', ('3.jpg', open('images\\3.jpg', 'rb'), 'image/jpg')),
                      ('0326095500', ('5.png', open('images\\5.png', 'rb'), 'image/png'))]

data2={'uids': ['0325933434','34','5', '0326095500']}
r = session.post("http://127.0.0.1:5000/predict", files=multiple_files,data=data2)
print(r.text)

session.close()