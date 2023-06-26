from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import numpy as np
import os
from PIL import Image
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
        print('Face detected with probability: {:8f}'.format(prob))
        return x_aligned
    else:
        print("No face detected")
        return None
    
def detect_faces(files):
    aligned = []
    for path in files:
        img = Image.open(path)
        aligned.append(detect_face(img))
        img.close()
    return aligned

# Calculate image embeddings
def calculate_embeddings(aligned):
    aligned = torch.stack(aligned).to(device)
    embeddings = resnet(aligned).detach().cpu().numpy()
    return embeddings

def get_embeddings(aligned):
    embeddings = []
    with torch.no_grad():
        for x_aligned in aligned:
            if x_aligned is None:
                embeddings.append(None)
                continue
            x_aligned = x_aligned.to(device)
            embedding = resnet(x_aligned.unsqueeze(0)).to('cpu').numpy()
            embeddings.append(embedding)
    return embeddings

def distance(embeddings1, embeddings2, distance_metric=0):
    if distance_metric==0:
        # Euclidian distance
        return np.linalg.norm(embeddings1 - embeddings2)
    elif distance_metric==1:
        # Distance based on cosine similarity
        dot = np.dot(embeddings1, embeddings2)
        norm = np.linalg.norm(embeddings1) * np.linalg.norm(embeddings2)
        similarity = dot / norm
        dist = np.arccos(similarity) / np.pi
    else:
        raise 'Undefined distance metric %d' % distance_metric

    return dist

