import os
import random
import string

def generate_random_string(length=8):
    """랜덤 문자열 생성"""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def rename_files_in_directory(directory):
    """디렉토리 내의 파일들을 랜덤한 이름으로 변경"""
    # 파일 이름 쌍 수집
    files = os.listdir(directory)
    file_pairs = {}

    for file in files:
        name, ext = os.path.splitext(file)
        if ext in ['.jpg', '.png', '.jpeg', '.bmp']:  # 이미지 파일 확장자
            if name not in file_pairs:
                file_pairs[name] = {'image': file}
            else:
                file_pairs[name]['image'] = file
        elif ext == '.txt':  # 텍스트 파일 확장자
            if name not in file_pairs:
                file_pairs[name] = {'text': file}
            else:
                file_pairs[name]['text'] = file
        elif ext == '.json':  # JSON 파일 확장자
            os.remove(os.path.join(directory, file))
            print(f"Deleted {file}")

    # 파일 이름 변경
    for name, pair in file_pairs.items():
        if 'image' in pair and 'text' in pair:
            new_name = generate_random_string()
            image_ext = os.path.splitext(pair['image'])[1]
            text_ext = os.path.splitext(pair['text'])[1]

            new_image_name = new_name + image_ext
            new_text_name = new_name + text_ext

            os.rename(os.path.join(directory, pair['image']), os.path.join(directory, new_image_name))
            os.rename(os.path.join(directory, pair['text']), os.path.join(directory, new_text_name))

            print(f"Renamed {pair['image']} and {pair['text']} to {new_image_name} and {new_text_name}")

rename_files_in_directory(r'C:\Capstone\data\obb\output')  # 디렉토리 경로를 정확히 지정하세요.