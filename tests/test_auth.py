import requests
url = "http://127.0.0.1:5000/auth/login"

session = requests.Session()

data={'username': "checkimage",
      'password': "123",
      "remember": True}

r = session.post(url,data=data)
print(r.text)
