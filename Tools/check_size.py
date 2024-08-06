import cv2

# 카메라 스트림 열기
cap = cv2.VideoCapture(1)  # 카메라 장치 번호를 지정합니다.

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
else:
    # 해상도 확인
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"카메라 해상도: {int(width)}x{int(height)}")

    # 카메라 스트림 닫기
    cap.release()
