from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import numpy as np
import os
from PIL import Image
import math
workers = 0 if os.name == 'nt' else 4

# Determine if an nvidia GPU is available

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# print('Running on device: {}'.format(device))

# Define MTCNN module

mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)

# Define Inception Resnet V1 module

resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Perfom MTCNN facial detection
def detect_face(img):
    x_aligned, prob = mtcnn(img, return_prob=True)
    if x_aligned is not None:
        # print('Face detected with probability: {:8f}'.format(prob))
        return x_aligned
    else:
        # print("No face detected")
        return None
    
def detect_faces(files):
    aligned = []
    for path in files:
        img = Image.open(path)
        aligned.append(detect_face(img))
    return aligned

# #### Calculate image embeddings
# 
# MTCNN will return images of faces all the same size, enabling easy batch processing with the Resnet recognition module. Here, since we only have a few images, we build a single batch and perform inference on it. 
# 
# For real datasets, code should be modified to control batch sizes being passed to the Resnet, particularly if being processed on a GPU. For repeated testing, it is best to separate face detection (using MTCNN) from embedding or classification (using InceptionResnetV1), as calculation of cropped faces or bounding boxes can then be performed a single time and detected faces saved for future use.

def calculate_embeddings(aligned):
    aligned = torch.stack(aligned).to(device)
    embeddings = resnet(aligned).detach().cpu().numpy()
    return embeddings

def distance(embeddings1, embeddings2, distance_metric=0):
    # embeddings1 = embeddings1.cpu().numpy()
    # embeddings2 = embeddings2.cpu().numpy() 
    if distance_metric==0:
        # Euclidian distance
        dist = np.linalg.norm(embeddings1 - embeddings2)
    elif distance_metric==1:
        # Distance based on cosine similarity
        dot = np.sum(np.multiply(embeddings1, embeddings2), axis=0)
        norm = np.linalg.norm(embeddings1, axis=0) * np.linalg.norm(embeddings2, axis=0)
        similarity = dot / norm
        dist = np.arccos(similarity) / math.pi
    else:
        raise 'Undefined distance metric %d' % distance_metric
    return dist



