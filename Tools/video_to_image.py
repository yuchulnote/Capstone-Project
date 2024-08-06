import cv2

def video_to_images(video_path, output_path, frame_interval):
    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Check if the video file was successfully opened
    if not video.isOpened():
        print("Error opening video file")
        return

    # Initialize variables
    frame_count = 0
    image_count = 0

    # Read the first frame
    success, frame = video.read()

    # Loop through the video frames
    while success:
        # Check if it's time to save an image
        if frame_count % frame_interval == 0:
            # Save the image
            image_path = f"{output_path}/image_{image_count}.jpg"
            cv2.imwrite(image_path, frame)
            image_count += 1

        # Read the next frame
        success, frame = video.read()
        frame_count += 1

    # Release the video file
    video.release()

# Example usage
video_path = r"C:\Users\yuddo\OneDrive\사진\카메라 앨범\WIN_20240620_01_11_14_Pro.mp4"
output_path = r"C:\Capstone\data\obb\output"
frame_interval = 5

video_to_images(video_path, output_path, frame_interval)