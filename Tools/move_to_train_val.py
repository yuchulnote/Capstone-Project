import os
import random
import shutil

# Set the source directory and destination directories
source_dir = r'C:\Capstone\data\er'
train_dir = r'C:\Capstone\data\retrain2\train'
val_dir = r'C:\Capstone\data\retrain2\val'

# Set the percentage split
train_percentage = 0.9
val_percentage = 0.1

# Get a list of all image files in the source directory
image_files = [f for f in os.listdir(source_dir) if f.endswith('.jpg')]

# Calculate the number of files to move for train and val
num_train_files = int(len(image_files) * train_percentage)
num_val_files = int(len(image_files) * val_percentage)

# Randomly select files for train and val
train_files = random.sample(image_files, num_train_files)
val_files = random.sample(image_files, num_val_files)

# Move the train files
for file in train_files:
    image_path = os.path.join(source_dir, file)
    txt_path = os.path.join(source_dir, file.replace('.jpg', '.txt'))
    shutil.move(image_path, train_dir)
    shutil.move(txt_path, train_dir)

# Move the val files
for file in val_files:
    image_path = os.path.join(source_dir, file)
    txt_path = os.path.join(source_dir, file.replace('.jpg', '.txt'))
    shutil.move(image_path, val_dir)
    shutil.move(txt_path, val_dir)