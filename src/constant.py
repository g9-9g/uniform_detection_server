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