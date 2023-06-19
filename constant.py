import os
from dotenv import load_dotenv
load_dotenv()


# Image database
URL = os.environ['URL']
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

if not os.environ['UPLOAD_FOLDER']:
    os.environ['UPLOAD_FOLDER'] = 'temp'

UPLOAD_FOLDER = os.environ['UPLOAD_FOLDER']
DATASET_FOLDER = os.environ['DATASET_FOLDER']
DEFAULT_STARTTIME = "2021-05-05"
ADMIN = {"username": os.environ["admin_username"], "pwd": os.environ["admin_pwd"]}


# Server
SECRET_KEY = os.environ['server_private_key']


# Roboflow
PROJECT_NAME = os.environ["project_name"]
API_KEY = os.environ["api_key"]

# Facenet
EUCLIDIAN_THRESHOLD = 0.85
COSINE_SIMILARITY_THRESHOLD = 0.28
# Sample
# sample = {
#     "token": "",
#     "UserId": "",
#     "UploadImg": [{
#         "URL": "http://102.123.92.277/ImageCPC1HN/File/Download?UserName=checkimage&UserId=0356116111&CallId=9622cd2b-e8c6-485e-9c1c-7c071975ce4d&FileName=3&Token=23C75BD161BD449E9CD4CFE72BC71470",
#         "UploadTime": "2022-05-04 15:45:18"
#         # "name": "",
#     }]
#     # file: 1 file
# }


# example_id = "0356116111"
