import os

# 텍스트 파일이 저장된 디렉토리 경로 설정
directory_path = r'C:\Capstone\data\retrain2\val'

# 디렉토리 내의 모든 텍스트 파일을 순회
for filename in os.listdir(directory_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory_path, filename)
        
        # 파일 읽기
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # 수정된 내용 저장할 리스트
        new_lines = []
        
        # 각 줄을 처리
        for line in lines:
            parts = line.strip().split()
            if parts[0] != '0':
                parts[0] = '0'
            new_line = ' '.join(parts)
            new_lines.append(new_line)
        
        # 파일 쓰기
        with open(file_path, 'w') as file:
            file.write('\n'.join(new_lines))

print("All labels have been updated.")