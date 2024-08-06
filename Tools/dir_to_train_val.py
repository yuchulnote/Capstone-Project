import os
import shutil
import random

def split_data(source_dir, train_dir, val_dir, split_ratio=0.9):
    # Ensure the target directories exist
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    # Get a list of files in the source directory
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

    # Shuffle the files
    random.shuffle(files)

    # Calculate the split index
    split_index = int(len(files) * split_ratio)

    # Split the files into train and val sets
    train_files = files[:split_index]
    val_files = files[split_index:]

    def move_files(file_list, target_dir, subset_name):
        for idx, file in enumerate(file_list):
            # Construct a new file name to avoid name collisions
            base, ext = os.path.splitext(file)
            new_file_name = f"{base}_{subset_name}_{idx}{ext}"
            shutil.move(os.path.join(source_dir, file), os.path.join(target_dir, new_file_name))

    # Move files to the respective directories
    move_files(train_files, train_dir, 'train')
    move_files(val_files, val_dir, 'val')

    print(f"Moved {len(train_files)} files to {train_dir}")
    print(f"Moved {len(val_files)} files to {val_dir}")

# Define the source, train, and validation directories
source_directory = r'C:\Capstone\data\obb\output'
train_directory = r'C:\Capstone\data\obb\train'
val_directory = r'C:\Capstone\data\obb\val'

# Split the data
split_data(source_directory, train_directory, val_directory)
