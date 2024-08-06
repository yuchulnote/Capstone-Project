import cv2
import numpy as np

# 클릭한 좌표를 저장할 리스트
image_points = []

# 마우스 콜백 함수
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        image_points.append([x, y])
        print(f"Point selected: ({x}, {y})")
        cv2.circle(param, (x, y), 5, (0, 255, 0), -1)

# 이미지 불러오기
image = cv2.imread(r'C:\Capstone\data\calibration\WIN_20240616_23_57_04_Pro.jpg')

# 이미지 크기 조정
resize_ratio = 0.5  # 이미지 축소 비율
resized_image = cv2.resize(image, (int(image.shape[1] * resize_ratio), int(image.shape[0] * resize_ratio)))

# 이미지 창 열기
cv2.namedWindow('Table')
cv2.setMouseCallback('Table', mouse_callback, resized_image)

print("테이블의 네 개의 꼭지점과 원점을 클릭하세요 (총 5점).")

while True:
    cv2.imshow('Table', resized_image)
    if len(image_points) == 5:  # 테이블 꼭지점과 원점 수
        break
    if cv2.waitKey(1) & 0xFF == 27:  # Esc 키를 누르면 종료
        break

cv2.destroyAllWindows()

if len(image_points) == 5:
    image_points = np.array(image_points, dtype=np.float32)
    image_points = image_points / resize_ratio  # 원본 이미지의 좌표로 변환
    print("클릭된 좌표:", image_points)
    # 좌표를 파일로 저장
    np.save('image_points.npy', image_points)
else:
    print("모든 점을 선택하지 않았습니다.")
