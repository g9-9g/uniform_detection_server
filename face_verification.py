from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import numpy as np
import pandas as pd
import os
import cv2
import preprocess
from PIL import Image
workers = 0 if os.name == 'nt' else 4

# Determine if an nvidia GPU is available

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))

# Define MTCNN module

mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)

# Define Inception Resnet V1 module

resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Perfom MTCNN facial detection

aligned = []
names = []
folder_name = 'D:/dev/project/pythonProject/temp_img/'
for (root, dirs, files) in os.walk(folder_name, topdown = True):
    for path in files:
        preprocess.autorotate(folder_name + path)
        preprocess.autoresize(folder_name + path)
        img = cv2.imread(folder_name + path)
        x_aligned, prob = mtcnn(img, return_prob=True)
        print(path, ' : ')
        if x_aligned is not None:
            print('Face detected with probability: {:8f}'.format(prob))
            aligned.append(x_aligned)
            names.append(path)
        else:
            print("No face detected") 

# #### Calculate image embeddings
# 
# MTCNN will return images of faces all the same size, enabling easy batch processing with the Resnet recognition module. Here, since we only have a few images, we build a single batch and perform inference on it. 
# 
# For real datasets, code should be modified to control batch sizes being passed to the Resnet, particularly if being processed on a GPU. For repeated testing, it is best to separate face detection (using MTCNN) from embedding or classification (using InceptionResnetV1), as calculation of cropped faces or bounding boxes can then be performed a single time and detected faces saved for future use.

aligned = torch.stack(aligned).to(device)
embeddings = resnet(aligned).detach().cpu()

# Print distance matrix for classes

dists = [[(e1 - e2).norm().item() for e2 in embeddings] for e1 in embeddings]
print(pd.DataFrame(dists, columns=names, index=names))


