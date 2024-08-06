import json
import os

def convert_to_yolo_obb(json_file_path, output_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        image_width = data['imageWidth']
        image_height = data['imageHeight']
        
        with open(output_file_path, 'w') as out_file:
            for shape in data['shapes']:
                class_index = 0
                points = shape['points']
                
                # Normalize points
                normalized_points = [(x / image_width, y / image_height) for x, y in points]
                
                # Flatten the list of points
                flattened_points = [coord for point in normalized_points for coord in point]
                
                # Create the YOLO OBB formatted string
                yolo_obb_format = f"{class_index} " + " ".join(f"{coord:.6f}" for coord in flattened_points) + "\n"
                
                out_file.write(yolo_obb_format)
    except PermissionError as e:
        print(f"PermissionError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def process_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            json_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename.replace('.json', '.txt'))
            convert_to_yolo_obb(json_file_path, output_file_path)

# Usage
input_directory = r'C:\Capstone\data\obb\output'  # 입력 디렉터리 경로
output_directory = r'C:\Capstone\data\obb\output'  # 출력 디렉터리 경로
process_directory(input_directory, output_directory)
