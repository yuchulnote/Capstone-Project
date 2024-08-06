import os
import shutil
from PIL import Image

def copy_images(json_directory, image_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(json_directory):
        if filename.endswith('.json'):
            json_filename = os.path.splitext(filename)[0]
            image_filename = json_filename + '.jpg'
            src_image_path = os.path.join(image_directory, image_filename)
            dest_image_path = os.path.join(output_directory, image_filename)

            if os.path.exists(src_image_path):
                shutil.copy(src_image_path, dest_image_path)
                print(f"Copied {src_image_path} to {dest_image_path}")
            else:
                print(f"Image file {src_image_path} not found, skipping.")

# Usage
json_directory = r'C:\Capstone\runs\obb\obb_1차'  # JSON 파일이 있는 디렉토리 경로
image_directory = r'C:\Capstone\data\obb\yet_train'  # 이미지 파일이 있는 디렉토리 경로
output_directory = r'C:\Capstone\runs\obb\obb_1차'  # 이미지를 복사할 출력 디렉토리 경로

copy_images(json_directory, image_directory, output_directory)
