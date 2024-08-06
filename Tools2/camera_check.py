import cv2
import pyudev

def get_camera_device_info():
    context = pyudev.Context()
    devices = []
    for device in context.list_devices(subsystem='video4linux'):
        if device.device_type == 'video':
            devices.append((device.device_node, device.get('ID_SERIAL_SHORT')))
    return devices

def match_camera_to_index():
    device_info = get_camera_device_info()
    camera_indices = []

    for device_node, serial in device_info:
        cap = cv2.VideoCapture(device_node)
        if cap.isOpened():
            index = device_node.split('/')[-1].replace('video', '')
            camera_indices.append((index, serial))
            cap.release()

    return camera_indices

if __name__ == "__main__":
    cameras = match_camera_to_index()
    for index, serial in cameras:
        print(f"Camera Index: {index}, Serial: {serial}")
