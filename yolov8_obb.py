from ultralytics import YOLO
import cv2
import numpy as np
import os
import random
import string

# Load a model
model = YOLO("yolov8n-obb.yaml")  # build a new model from YAML
model = YOLO("yolov8n-obb.pt")  # load a pretrained model (recommended for training)
model = YOLO("yolov8n-obb.yaml").load("yolov8n.pt")  # build from YAML and transfer weights

predict_model = YOLO('yolov8n-obb.pt')
predict_model = YOLO(r'C:\Capstone\runs\obb\train7\weights\best.pt')
predict_model.names

def train_model():
    results = model.train(data=r'C:\Capstone\obb.yaml',
                        epochs=300,
                        imgsz=(640, 640))
    
    return results


def predict():
    # source = r'C:\Capstone\data\obb\yet_train'
    source = r'C:\Capstone\테스트'
    predicted_results = predict_model(source, name='obb_test', save=True, save_txt=True, show_labels=True, show_conf=True, stream=True)
    for r in predicted_results:
        boxes = r.boxes
        masks = r.masks
        probs = r.probs

if __name__ == '__main__':
    train_model()
    # predict()