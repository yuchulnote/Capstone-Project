import json
import os
from PIL import Image

def yolo_obb_to_json(yolo_obb_file, json_output_file, image_file):
    # 이미지 크기 가져오기
    with Image.open(image_file) as img:
        image_width, image_height = img.size

    shapes = []
    
    with open(yolo_obb_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            class_index = int(parts[0])
            points = [(float(parts[i]) * image_width, float(parts[i+1]) * image_height) for i in range(1, len(parts), 2)]
            
            shape = {
                "label": "cup",  # class_index를 실제 클래스 이름으로 매핑하는 부분입니다.
                "text": "",
                "points": points,
                "group_id": None,
                "shape_type": "polygon",
                "flags": {}
            }
            shapes.append(shape)
    
    data = {
        "version": "0.3.3",
        "flags": {},
        "shapes": shapes,
        "imagePath": os.path.basename(image_file),
        "imageData": None,
        "imageHeight": image_height,
        "imageWidth": image_width
    }
    
    with open(json_output_file, 'w') as f:
        json.dump(data, f, indent=4)

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            yolo_obb_file = os.path.join(directory, filename)
            json_output_file = os.path.join(directory, filename.replace('.txt', '.json'))
            image_file = os.path.join(directory, filename.replace('.txt', '.jpg'))
            
            if os.path.exists(image_file):
                yolo_obb_to_json(yolo_obb_file, json_output_file, image_file)
            else:
                print(f"Image file {image_file} not found, skipping.")

# Usage
directory = r'C:\Capstone\data\obb\temp'  # 입력 디렉터리 경로
process_directory(directory)
