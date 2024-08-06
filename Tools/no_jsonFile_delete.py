import os

def delete_files_without_json(path):
    # 모든 JSON 파일의 이름을 수집 (확장자 없이)
    json_files = {os.path.splitext(filename)[0] for filename in os.listdir(path) if filename.endswith('.json')}
    
    # 디렉토리 내 모든 파일을 순회
    for filename in os.listdir(path):
        # 파일 경로 생성
        file_path = os.path.join(path, filename)
        
        # 파일 이름에서 확장자를 제거한 이름을 추출
        name_without_ext = os.path.splitext(filename)[0]
        
        # 현재 파일이 JSON 파일이나 JSON 파일과 일치하는 이미지 파일이면 삭제하지 않음
        if filename.endswith('.json') or name_without_ext in json_files:
            continue
        else:
            # 파일이 JSON 파일이나 JSON과 일치하는 이미지 파일이 아니면 삭제
            if os.path.isfile(file_path):
                os.remove(file_path)

# Usage example
delete_files_without_json(r'C:\Capstone\data\obb\output')
