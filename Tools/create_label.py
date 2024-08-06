import cv2
import os

def create_label_file(image_path, label_dir):
    # 이미지 파일 이름에서 확장자를 제거하여 라벨 파일 이름 생성
    label_file_name = os.path.splitext(os.path.basename(image_path))[0] + '.txt'
    label_file_path = os.path.join(label_dir, label_file_name)

    # 이미지 읽기
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image {image_path}")
        return

    # 이미지 크기 추출
    height, width = image.shape[:2]

    # 바운딩 박스 정보 생성 (이미지 전체를 바운딩 박스로 간주)
    class_id = 0  # 클래스 ID는 0으로 설정 (필요에 따라 변경 가능)
    x_center = width / 2.0 / width
    y_center = height / 2.0 / height
    bbox_width = 1.0  # 이미지 전체 너비를 바운딩 박스로 설정
    bbox_height = 1.0  # 이미지 전체 높이를 바운딩 박스로 설정

    # 라벨 파일 작성
    with open(label_file_path, 'w') as label_file:
        label_file.write(f'{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n')

    print(f"Label file created: {label_file_path}")

def process_directory(image_dir, label_dir):
    # 라벨 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)

    # 이미지 디렉토리 내의 모든 파일 처리
    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)
        if os.path.isfile(image_path):
            create_label_file(image_path, label_dir)

# 이미지와 라벨 디렉토리 경로 설정
image_directory = r'C:\Capstone\data\segmentation'
label_directory = r'C:\Capstone\data\segmentation'

# 디렉토리 내의 모든 이미지 파일에 대해 라벨 파일 생성
process_directory(image_directory, label_directory)
